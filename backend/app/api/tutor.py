"""
智能辅导API
直接调用 TutorAgent，避免 LangGraph 多层路由延迟
"""
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timezone

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ..agents import TutorAgent
from ..core.logger import setup_logger
from ..models.database import get_db
from ..models.tutor_qa import TutorQAModel
from ..services.path_adjustment_engine import maybe_check_path_adjustment
from .auth import get_current_student_id, require_auth

logger = setup_logger()

router = APIRouter()


class TutorRequest(BaseModel):
    """辅导请求（支持纯文本或图文数组）"""
    student_id: str
    question: Union[str, List[Dict[str, Any]]]
    context: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None
    provider: Optional[str] = None  # bigmodel / deepseek / openai / spark
    rag_active: bool = True  # 是否启用画像/知识库检索增强
    task: str = "answer_question"  # answer_question / hint / encourage / explain_code / explain_error
    mode: str = "socratic"  # socratic / normal


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
async def ask_tutor(request: TutorRequest, db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    """向AI辅导助手提问（苏格拉底式教学）—— 直接调用 TutorAgent，避免 LangGraph 多层路由延迟"""
    session_id = request.session_id or f"{request.student_id}_default"

    # rag_active=True 时拉取学生画像，向 prompt 注入薄弱点与认知风格
    profile_for_prompt: Dict[str, Any] = {}
    if request.rag_active:
        try:
            from ..models.student import StudentProfileModel
            p = db.query(StudentProfileModel).filter(StudentProfileModel.student_id == request.student_id).first()
            if p:
                profile_for_prompt = {
                    "weak_areas": p.weak_areas or [],
                    "cognitive_style": p.cognitive_style or {},
                    "interest_areas": p.interest_areas or [],
                }
        except Exception as e:
            logger.warning(f"获取画像失败: {e}")
            profile_for_prompt = {}

    result: Optional[Dict[str, Any]] = None
    try:
        result = await asyncio.wait_for(
            _tutor_agent.process({
                "task": request.task,
                "session_id": session_id,
                "question": request.question,
                "language": request.context.get("language", "C") if request.context else "C",
                "profile": profile_for_prompt,
                "llm_provider": request.provider,
                "mode": request.mode,
            }),
            timeout=30.0,
        )
        if result.get("status") == "success":
            answer = result.get("answer", "很抱歉，我没有理解你的问题，可以再说一遍吗？")
        elif result.get("status") == "blocked":
            answer = result.get("reason", "内容被安全过滤，请换种方式提问。")
        else:
            answer = "服务暂时不可用，请稍后再试。"
    except asyncio.TimeoutError:
        answer = "模型响应超时，请重试或切换到WebSocket流式模式。"
    except Exception as e:
        logger.error(f"辅导问答异常: {e}")
        answer = "服务暂时不可用，请稍后再试。"

    # 持久化问答记录
    try:
        meta: Dict[str, Any] = {"rag_active": request.rag_active}
        if not isinstance(request.question, str):
            meta["raw"] = request.question
        qa = TutorQAModel(
            student_id=request.student_id,
            session_id=session_id,
            question=str(request.question) if isinstance(request.question, str) else "[多模态输入]",
            answer=answer,
            question_meta=meta,
            profile_snapshot=profile_for_prompt or None,
            response_type="explanation",
            blocked=result.get("status") == "blocked" if result else False,
            block_reason=result.get("reason") if result and result.get("status") == "blocked" else None,
            llm_provider=request.provider,
        )
        db.add(qa)
        db.commit()

        # 检查是否需要调整路径
        await maybe_check_path_adjustment(request.student_id, db)
    except Exception as e:
        logger.warning(f"问答记录持久化失败: {e}")
        db.rollback()

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
            raw = await websocket.receive_text()
            if len(raw) > 10_000:
                await manager.send_message(session_id, {
                    "type": "error",
                    "message": "消息过长（超过10KB），请缩短后重试",
                })
                continue
            import json as _json
            try:
                data = _json.loads(raw)
            except Exception:
                await manager.send_message(session_id, {
                    "type": "error",
                    "message": "消息格式无效，请发送合法JSON",
                })
                continue
            message_type = data.get("type", "message")

            if message_type == "message":
                question = data.get("content", "")
                provider = data.get("provider")
                rag_active = bool(data.get("rag_active", True))
                mode = data.get("mode", "socratic")

                # Step 1: planner —— 任务拆解 / 安全检查
                await manager.send_message(session_id, {
                    "type": "agent_step",
                    "step": "planner",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })

                # 输入安全校验
                safety = SafetyGuard.check_input(question)
                if not safety["safe"]:
                    await manager.send_message(session_id, {
                        "type": "chunk",
                        "content": "【内容安全提醒】输入包含敏感内容，请修改后重试。",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    })
                    await manager.send_message(session_id, {"type": "complete", "timestamp": datetime.now(timezone.utc).isoformat()})
                    continue

                # 获取 LLM 实例（支持动态切换）
                try:
                    llm = LLMFactory.get_llm(provider) if provider else LLMFactory.get_default_llm()
                except Exception as e:
                    await manager.send_message(session_id, {
                        "type": "chunk",
                        "content": f"模型加载失败：{e}",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    })
                    await manager.send_message(session_id, {"type": "complete", "timestamp": datetime.now(timezone.utc).isoformat()})
                    continue

                # rag_active=True 时拉取学生画像注入 prompt
                profile_snippet = ""
                profile_snapshot: Optional[Dict[str, Any]] = None
                if rag_active:
                    try:
                        from ..models.database import SessionLocal as _SL
                        from ..models.student import StudentProfileModel
                        _db = _SL()
                        try:
                            p = _db.query(StudentProfileModel).filter(StudentProfileModel.student_id == student_id).first()
                            if p:
                                weak = (p.weak_areas or [])[:5]
                                style = (p.cognitive_style or {}).get("primary", "visual")
                                interests = (p.interest_areas or [])[:3]
                                profile_snapshot = {
                                    "weak_areas": weak,
                                    "cognitive_style": p.cognitive_style or {},
                                    "interest_areas": interests,
                                }
                                profile_snippet = (
                                    f"\n[RAG 画像参考] 薄弱点：{weak}；认知风格：{style}；兴趣领域：{interests}\n"
                                    "请在引导式提问中针对薄弱点出题，措辞贴合该认知风格。"
                                )
                        finally:
                            _db.close()
                    except Exception as e:
                        logger.warning(f"WebSocket画像获取失败: {e}")
                        profile_snippet = ""

                # 构建消息历史
                history = _tutor_agent.session_histories.setdefault(session_id, [])
                if mode == "socratic":
                    prompt = SafetyGuard.sanitize_prompt(
                        f"学生提问：{question}\n{profile_snippet}请用苏格拉底式提问回应：不直接给答案，而是通过 2-3 个引导性问题，帮助学生自己思考出答案。最后可以给学生一句简短鼓励。"
                    )
                    system_prompt = _tutor_agent.get_system_prompt()
                else:
                    prompt = SafetyGuard.sanitize_prompt(
                        f"学生提问：{question}\n{profile_snippet}请直接、清晰地回答学生的问题，给出准确的知识讲解和实用建议。"
                    )
                    system_prompt = _tutor_agent.get_normal_system_prompt()
                messages = [
                    {"role": "system", "content": system_prompt},
                    *history,
                    {"role": "user", "content": prompt},
                ]

                # Step 2: worker —— 调用 LLM 真实流式生成
                await manager.send_message(session_id, {
                    "type": "agent_step",
                    "step": "worker",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })

                # 真实流式输出
                full_answer = ""
                client_disconnected = False
                logger.info(f"Starting stream with llm={llm.__class__.__name__}, model={getattr(llm, 'model', 'unknown')}")
                logger.info(f"Messages count: {len(messages)}")
                try:
                    chunk_count = 0
                    async for chunk in llm.astream(messages, temperature=0.6, max_tokens=1024):
                        chunk_count += 1
                        if not chunk:
                            continue
                        full_answer += chunk
                        logger.debug(f"Chunk {chunk_count}: {chunk[:30]}")
                        try:
                            await manager.send_message(session_id, {
                                "type": "chunk",
                                "content": chunk,
                                "timestamp": datetime.now(timezone.utc).isoformat(),
                            })
                        except Exception:
                            client_disconnected = True
                            break
                except Exception as e:
                    logger.error(f"Stream error: {e}")
                    if not full_answer:
                        full_answer = "流式输出异常，请稍后重试"
                        if not client_disconnected:
                            await manager.send_message(session_id, {
                                "type": "chunk",
                                "content": full_answer,
                                "timestamp": datetime.now(timezone.utc).isoformat(),
                            })

                logger.info(f"Stream complete. total_chunks={chunk_count}, full_answer_len={len(full_answer)}")
                # Step 3: critic —— 输出安全审核
                await manager.send_message(session_id, {
                    "type": "agent_step",
                    "step": "critic",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
                out_safe = SafetyGuard.check_output(full_answer)
                if not out_safe.get("safe", True):
                    full_answer = "[内容已拦截] 回答包含不适宜内容，请换种方式提问。"
                    await manager.send_message(session_id, {
                        "type": "chunk",
                        "content": "\n" + full_answer,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    })

                # 更新会话历史
                history.append({"role": "user", "content": question})
                history.append({"role": "assistant", "content": full_answer})
                if len(history) > 20:
                    history[:] = history[-20:]

                # 检测学习状态并推送
                learning_state = _tutor_agent._detect_learning_state(history)
                await manager.send_message(session_id, {
                    "type": "learning_state",
                    "state": learning_state["state"],
                    "hint": learning_state["hint"],
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })

                # 持久化问答记录
                try:
                    from ..models.database import SessionLocal
                    db = SessionLocal()
                    try:
                        qa = TutorQAModel(
                            student_id=student_id,
                            session_id=session_id,
                            question=question,
                            answer=full_answer,
                            question_meta={"rag_active": rag_active},
                            profile_snapshot=profile_snapshot,
                            response_type="explanation",
                            llm_provider=provider,
                        )
                        db.add(qa)
                        db.commit()
                    finally:
                        db.close()
                except Exception as e:
                    logger.warning(f"WebSocket问答记录持久化失败: {e}")

                await manager.send_message(session_id, {
                    "type": "complete",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })

            elif message_type == "ping":
                await manager.send_message(session_id, {"type": "pong"})

    except WebSocketDisconnect:
        manager.disconnect(session_id)
        _tutor_agent.clear_session(session_id)


@router.get("/session/{session_id}/history")
async def get_session_history(session_id: str, db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    """获取辅导会话历史（优先从数据库读取持久化记录）"""
    # 从数据库读取该 session 的问答记录
    records = (
        db.query(TutorQAModel)
        .filter(TutorQAModel.session_id == session_id)
        .order_by(TutorQAModel.created_at.asc())
        .limit(100)
        .all()
    )
    if records:
        messages = []
        for r in records:
            messages.append({"role": "user", "content": r.question})
            messages.append({"role": "assistant", "content": r.answer})
        return {
            "status": "success",
            "session_id": session_id,
            "source": "database",
            "messages": messages,
        }
    # fallback 到内存历史
    history = _tutor_agent.session_histories.get(session_id, [])
    messages = []
    for h in history:
        messages.append({"role": h["role"], "content": h["content"]})
    return {
        "status": "success",
        "session_id": session_id,
        "source": "memory",
        "messages": messages,
    }


@router.get("/qa-history/{student_id}")
async def get_student_qa_history(
    student_id: str,
    session_id: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    _current: str = Depends(require_auth),
):
    """获取学生的辅导问答历史（用于后续分析和优化）"""
    if _current != student_id:
        raise HTTPException(status_code=403, detail="无权访问其他学生的问答记录")
    query = db.query(TutorQAModel).filter(TutorQAModel.student_id == student_id)
    if session_id:
        query = query.filter(TutorQAModel.session_id == session_id)
    records = query.order_by(TutorQAModel.created_at.desc()).limit(limit).all()
    return {
        "status": "success",
        "student_id": student_id,
        "count": len(records),
        "data": [
            {
                "id": r.id,
                "session_id": r.session_id,
                "question": r.question,
                "answer": r.answer,
                "response_type": r.response_type,
                "blocked": r.blocked,
                "llm_provider": r.llm_provider,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in records
        ],
    }


@router.post("/qa-feedback/{qa_id}")
async def submit_qa_feedback(
    qa_id: int,
    feedback: str,  # like / dislike
    db: Session = Depends(get_db),
    _current: str = Depends(require_auth),
):
    """学生对问答记录提交反馈（点赞/点踩）"""
    qa = db.query(TutorQAModel).filter(TutorQAModel.id == qa_id).first()
    if not qa:
        raise HTTPException(status_code=404, detail="QA record not found")
    qa.feedback = feedback
    db.commit()
    return {"status": "success", "message": "Feedback recorded"}


@router.delete("/session/{session_id}")
async def delete_session(session_id: str, db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    """删除指定会话的所有问答记录"""
    try:
        deleted = db.query(TutorQAModel).filter(
            TutorQAModel.session_id == session_id,
            TutorQAModel.student_id == _current,
        ).delete()
        db.commit()
        return {"status": "success", "deleted": deleted}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")
