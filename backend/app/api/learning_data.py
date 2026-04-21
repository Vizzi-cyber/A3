"""
学习数据上报API
- 学习记录、测验结果、进度
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from sqlalchemy.orm import Session
from ..models.database import get_db
from ..models.knowledge import LearningRecordModel, QuizResultModel

router = APIRouter()


class LearningRecordRequest(BaseModel):
    student_id: str
    kp_id: str
    action: str  # watch / read / practice / review
    duration: int = 0
    progress: float = 0.0
    score: Optional[float] = None
    meta: Dict[str, Any] = {}


class QuizResultRequest(BaseModel):
    student_id: str
    kp_id: str
    total_questions: int
    correct_count: int
    score: float
    weak_tags: List[str] = []
    time_spent: int = 0
    answers: List[Dict[str, Any]] = []


@router.post("/record")
async def record_learning(request: LearningRecordRequest, db: Session = Depends(get_db)):
    """上报学习记录"""
    record_id = f"lr_{datetime.now().timestamp()}"
    record = LearningRecordModel(
        record_id=record_id,
        student_id=request.student_id,
        kp_id=request.kp_id,
        action=request.action,
        duration=request.duration,
        progress=request.progress,
        score=request.score,
        meta=request.meta,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return {"status": "success", "record_id": record_id}


@router.post("/quiz")
async def record_quiz(request: QuizResultRequest, db: Session = Depends(get_db)):
    """上报测验结果"""
    quiz_id = f"qz_{datetime.now().timestamp()}"
    quiz = QuizResultModel(
        quiz_id=quiz_id,
        student_id=request.student_id,
        kp_id=request.kp_id,
        total_questions=request.total_questions,
        correct_count=request.correct_count,
        score=request.score,
        weak_tags=request.weak_tags,
        time_spent=request.time_spent,
        answers=request.answers,
    )
    db.add(quiz)
    db.commit()
    db.refresh(quiz)
    return {"status": "success", "quiz_id": quiz_id}


@router.get("/{student_id}/history")
async def get_learning_history(student_id: str, limit: int = 50, db: Session = Depends(get_db)):
    """获取学生学习历史"""
    records = (
        db.query(LearningRecordModel)
        .filter(LearningRecordModel.student_id == student_id)
        .order_by(LearningRecordModel.created_at.desc())
        .limit(limit)
        .all()
    )
    quizzes = (
        db.query(QuizResultModel)
        .filter(QuizResultModel.student_id == student_id)
        .order_by(QuizResultModel.created_at.desc())
        .limit(limit)
        .all()
    )
    return {
        "status": "success",
        "student_id": student_id,
        "records": [
            {
                "record_id": r.record_id,
                "kp_id": r.kp_id,
                "action": r.action,
                "duration": r.duration,
                "progress": r.progress,
                "score": r.score,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in records
        ],
        "quizzes": [
            {
                "quiz_id": q.quiz_id,
                "kp_id": q.kp_id,
                "score": q.score,
                "correct_count": q.correct_count,
                "total_questions": q.total_questions,
                "weak_tags": q.weak_tags,
                "created_at": q.created_at.isoformat() if q.created_at else None,
            }
            for q in quizzes
        ],
    }
