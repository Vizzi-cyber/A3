"""
学习日志与自我反思API
- 学习日志自动记录
- 反思记录存储与查询
- 学习复盘数据接口
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from sqlalchemy.orm import Session
from ..models.database import get_db
from ..models.log_reflection import LearningLogModel, ReflectionModel

router = APIRouter()


# ---------- 学习日志 ----------

@router.get("/{student_id}/logs")
async def get_learning_logs(student_id: str, date: Optional[str] = None, db: Session = Depends(get_db)):
    """获取学习日志"""
    query = db.query(LearningLogModel).filter(LearningLogModel.student_id == student_id)
    if date:
        query = query.filter(LearningLogModel.date == date)
    logs = query.order_by(LearningLogModel.date.desc()).limit(100).all()
    return {
        "status": "success",
        "data": [
            {
                "log_id": l.log_id,
                "date": l.date,
                "total_duration": l.total_duration,
                "kp_count": l.kp_count,
                "quiz_count": l.quiz_count,
                "avg_score": l.avg_score,
                "mistakes": l.mistakes,
                "path_progress": l.path_progress,
                "completed_tasks": l.completed_tasks,
                "timeline": l.timeline,
            }
            for l in logs
        ],
    }


class UpsertLogRequest(BaseModel):
    student_id: str
    date: str
    total_duration: int = 0
    kp_count: int = 0
    quiz_count: int = 0
    avg_score: float = 0.0
    mistakes: List[str] = []
    path_progress: float = 0.0
    completed_tasks: List[str] = []
    timeline: List[Dict[str, Any]] = []


@router.post("/logs/upsert")
async def upsert_learning_log(request: UpsertLogRequest, db: Session = Depends(get_db)):
    """创建或更新学习日志"""
    existing = db.query(LearningLogModel).filter(
        LearningLogModel.student_id == request.student_id,
        LearningLogModel.date == request.date,
    ).first()
    if existing:
        existing.total_duration = request.total_duration
        existing.kp_count = request.kp_count
        existing.quiz_count = request.quiz_count
        existing.avg_score = request.avg_score
        existing.mistakes = request.mistakes
        existing.path_progress = request.path_progress
        existing.completed_tasks = request.completed_tasks
        existing.timeline = request.timeline
        db.commit()
        return {"status": "success", "message": "Log updated"}
    log = LearningLogModel(
        log_id=f"log_{request.student_id}_{request.date}",
        student_id=request.student_id,
        date=request.date,
        total_duration=request.total_duration,
        kp_count=request.kp_count,
        quiz_count=request.quiz_count,
        avg_score=request.avg_score,
        mistakes=request.mistakes,
        path_progress=request.path_progress,
        completed_tasks=request.completed_tasks,
        timeline=request.timeline,
    )
    db.add(log)
    db.commit()
    return {"status": "success", "message": "Log created"}


# ---------- 反思记录 ----------

class ReflectionCreateRequest(BaseModel):
    student_id: str
    date: str
    content: str
    mood: str = "neutral"
    tags: List[str] = []
    ai_feedback: Optional[str] = None


@router.post("/reflections/create")
async def create_reflection(request: ReflectionCreateRequest, db: Session = Depends(get_db)):
    """创建反思记录"""
    reflection_id = f"ref_{request.student_id}_{request.date}"
    existing = db.query(ReflectionModel).filter(ReflectionModel.reflection_id == reflection_id).first()
    if existing:
        existing.content = request.content
        existing.mood = request.mood
        existing.tags = request.tags
        existing.ai_feedback = request.ai_feedback
        db.commit()
        return {"status": "success", "message": "Reflection updated", "reflection_id": reflection_id}
    ref = ReflectionModel(
        reflection_id=reflection_id,
        student_id=request.student_id,
        date=request.date,
        content=request.content,
        mood=request.mood,
        tags=request.tags,
        ai_feedback=request.ai_feedback,
    )
    db.add(ref)
    db.commit()
    return {"status": "success", "reflection_id": reflection_id}


@router.get("/{student_id}/reflections")
async def get_reflections(student_id: str, limit: int = 30, db: Session = Depends(get_db)):
    """获取反思记录列表"""
    refs = (
        db.query(ReflectionModel)
        .filter(ReflectionModel.student_id == student_id)
        .order_by(ReflectionModel.date.desc())
        .limit(limit)
        .all()
    )
    return {
        "status": "success",
        "data": [
            {
                "reflection_id": r.reflection_id,
                "date": r.date,
                "content": r.content,
                "mood": r.mood,
                "tags": r.tags,
                "ai_feedback": r.ai_feedback,
            }
            for r in refs
        ],
    }


@router.get("/{student_id}/review")
async def get_learning_review(student_id: str, db: Session = Depends(get_db)):
    """学习复盘数据接口（聚合日志与反思）"""
    logs = (
        db.query(LearningLogModel)
        .filter(LearningLogModel.student_id == student_id)
        .order_by(LearningLogModel.date.desc())
        .limit(7)
        .all()
    )
    refs = (
        db.query(ReflectionModel)
        .filter(ReflectionModel.student_id == student_id)
        .order_by(ReflectionModel.date.desc())
        .limit(7)
        .all()
    )
    total_duration = sum(l.total_duration for l in logs)
    avg_score = sum(l.avg_score for l in logs) / len(logs) if logs else 0.0
    return {
        "status": "success",
        "student_id": student_id,
        "review_period_days": len(logs),
        "summary": {
            "total_duration": total_duration,
            "total_kps": sum(l.kp_count for l in logs),
            "total_quizzes": sum(l.quiz_count for l in logs),
            "avg_score": round(avg_score, 2),
            "reflection_count": len(refs),
        },
        "daily_logs": [
            {
                "date": l.date,
                "duration": l.total_duration,
                "kp_count": l.kp_count,
                "quiz_count": l.quiz_count,
                "avg_score": l.avg_score,
                "mistakes": l.mistakes,
                "path_progress": l.path_progress,
            }
            for l in logs
        ],
        "reflections": [
            {
                "date": r.date,
                "mood": r.mood,
                "tags": r.tags,
                "content_preview": r.content[:100] + "..." if r.content and len(r.content) > 100 else r.content,
            }
            for r in refs
        ],
    }
