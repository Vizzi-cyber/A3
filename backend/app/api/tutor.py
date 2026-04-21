"""
智能辅导API
直接调用 TutorAgent，避免 LangGraph 多层路由延迟
"""
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from ..agents import TutorAgent
from .auth import get_current_student_id, require_auth

router = APIRouter()


class TutorRequest(BaseModel):
    """辅导请求（支持纯文本或图文数组）"""
    student_id: str
    question: Union[str, List[Dict[str, Any]]]
    context: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None


class TutorResponse(BaseModel):
    """辅导响应"""
    response: str
    response_type: str
    resources: Optional[List[Dict]] = None
    follow_up_questions: Optional[List[str]] = None


# WebSocket连接管理
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]

    async def send_message(self, session_id: str, message: Dict):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_json(message)


manager = ConnectionManager()

# 全局 TutorAgent 实例（用于维护 WebSocket 会话历史）
_tutor_agent = TutorAgent()


@router.post("/ask", response_model=TutorResponse)
async def ask_tutor(request: TutorRequest, _current: str = Depends(require_auth)):
    """向AI辅导助手提问（苏格拉底式教学）—— 直接调用 TutorAgent，避免 LangGraph 多层路由延迟"""
    session_id = request.session_id or f"{request.student_id}_default"

    try:
        result = await asyncio.wait_for(
            _tutor_agent.process({
                "task": "answer_question",
                "session_id": session_id,
                "question": request.question,
                "profile": {},
            }),
            timeout=15.0,
        )
        if result.get("status") == "success":
            answer = result.get("answer", "很抱歉，我没有理解你的问题，可以再说一遍吗？")
        else:
            answer = "服务暂时不可用，请稍后再试。"
    except asyncio.TimeoutError:
        answer = "思考时间较长，请稍后再试或简化问题。"

    return TutorResponse(
        response=answer,
        response_type="question" if "?" in answer else "explanation",
        follow_up_questions=["你能举一个具体的例子吗？"] if "?" in answer else None,
    )


@router.websocket("/ws/{session_id}")
async def tutor_websocket(websocket: WebSocket, session_id: str):
    """WebSocket实时辅导，支持流式输出"""
    await manager.connect(session_id, websocket)

    try:
        while True:
            data = await websocket.receive_json()
            message_type = data.get("type", "message")

            if message_type == "message":
                question = data.get("content", "")
                student_id = data.get("student_id", "anonymous")

                # 调用 TutorAgent 获取回答（带超时保护）
                try:
                    result = await asyncio.wait_for(
                        _tutor_agent.process({
                            "task": "answer_question",
                            "session_id": session_id,
                            "question": question,
                            "profile": {},
                        }),
                        timeout=15.0,
                    )
                    answer = result.get("answer", "") if result.get("status") == "success" else "服务暂时不可用"
                except asyncio.TimeoutError:
                    answer = "思考时间较长，请稍后再试或简化问题。"

                # 模拟流式输出（按句子拆分）
                parts = answer.replace("。", "。\n").replace("？", "？\n").replace("！", "！\n").split("\n")
                parts = [p.strip() for p in parts if p.strip()]
                if len(parts) <= 1:
                    parts = [answer[i:i+30] for i in range(0, len(answer), 30)]

                for part in parts:
                    await manager.send_message(session_id, {
                        "type": "chunk",
                        "content": part,
                        "timestamp": datetime.now().isoformat(),
                    })
                    await __import__("asyncio").sleep(0.2)

                await manager.send_message(session_id, {
                    "type": "complete",
                    "timestamp": datetime.now().isoformat(),
                })

            elif message_type == "ping":
                await manager.send_message(session_id, {"type": "pong"})

    except WebSocketDisconnect:
        manager.disconnect(session_id)
        _tutor_agent.clear_session(session_id)


@router.get("/session/{session_id}/history")
async def get_session_history(session_id: str):
    """获取辅导会话历史"""
    history = _tutor_agent.session_histories.get(session_id, [])
    messages = []
    for h in history:
        messages.append({"role": h["role"], "content": h["content"]})
    return {
        "status": "success",
        "session_id": session_id,
        "messages": messages,
    }
