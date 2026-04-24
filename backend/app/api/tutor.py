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
    provider: Optional[str] = None  # bigmodel / deepseek / openai / spark


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
                "llm_provider": request.provider,
            }),
            timeout=15.0,
        )
        if result.get("status") == "success":
            answer = result.get("answer", "很抱歉，我没有理解你的问题，可以再说一遍吗？")
        elif result.get("status") == "blocked":
            answer = result.get("reason", "内容被安全过滤，请换种方式提问。")
        else:
            answer = "服务暂时不可用，请稍后再试。"
    except asyncio.TimeoutError:
        answer = "模型响应超时，请重试或切换到WebSocket流式模式。"

    return TutorResponse(
        response=answer,
        response_type="question" if "?" in answer else "explanation",
        follow_up_questions=["你能举一个具体的例子吗？"] if "?" in answer else None,
    )


@router.websocket("/ws/{session_id}")
async def tutor_websocket(websocket: WebSocket, session_id: str):
    """WebSocket实时辅导，支持真实 LLM 流式输出与多模型切换"""
    from ..services.llm_factory import LLMFactory
    from ..core.safety import SafetyGuard
    from .auth import verify_token_for_websocket

    # WebSocket 认证：从 query param 读取 token
    token = websocket.query_params.get("token")
    student_id = verify_token_for_websocket(token)
    if not student_id:
        await websocket.close(code=1008, reason="Unauthorized")
        return

    await manager.connect(session_id, websocket)

    try:
        while True:
            data = await websocket.receive_json()
            message_type = data.get("type", "message")

            if message_type == "message":
                question = data.get("content", "")
                student_id = data.get("student_id", "anonymous")
                provider = data.get("provider")

                # 输入安全校验
                safety = SafetyGuard.check_input(question)
                if not safety["safe"]:
                    await manager.send_message(session_id, {
                        "type": "chunk",
                        "content": "【内容安全提醒】输入包含敏感内容，请修改后重试。",
                        "timestamp": datetime.now().isoformat(),
                    })
                    await manager.send_message(session_id, {"type": "complete", "timestamp": datetime.now().isoformat()})
                    continue

                # 获取 LLM 实例（支持动态切换）
                try:
                    llm = LLMFactory.get_llm(provider) if provider else _tutor_agent.llm
                except Exception as e:
                    await manager.send_message(session_id, {
                        "type": "chunk",
                        "content": f"模型加载失败：{e}",
                        "timestamp": datetime.now().isoformat(),
                    })
                    await manager.send_message(session_id, {"type": "complete", "timestamp": datetime.now().isoformat()})
                    continue

                # 构建消息历史
                history = _tutor_agent.session_histories.setdefault(session_id, [])
                prompt = SafetyGuard.sanitize_prompt(
                    f"学生提问：{question}\n请用苏格拉底式提问回应：不直接给答案，而是通过 2-3 个引导性问题，帮助学生自己思考出答案。最后可以给学生一句简短鼓励。"
                )
                messages = [
                    {"role": "system", "content": _tutor_agent.get_system_prompt()},
                    *history,
                    {"role": "user", "content": prompt},
                ]

                # 真实流式输出
                full_answer = ""
                try:
                    async for chunk in llm.astream(messages, temperature=0.6, max_tokens=1024):
                        if not chunk:
                            continue
                        full_answer += chunk
                        await manager.send_message(session_id, {
                            "type": "chunk",
                            "content": chunk,
                            "timestamp": datetime.now().isoformat(),
                        })
                except Exception as e:
                    if not full_answer:
                        full_answer = f"流式输出异常：{str(e)}"
                        await manager.send_message(session_id, {
                            "type": "chunk",
                            "content": full_answer,
                            "timestamp": datetime.now().isoformat(),
                        })

                # 更新会话历史
                history.append({"role": "user", "content": question})
                history.append({"role": "assistant", "content": full_answer})
                if len(history) > 20:
                    history[:] = history[-20:]

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
