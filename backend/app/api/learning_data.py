"""
学习数据上报API
- 学习记录、测验结果、进度
"""
import secrets

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from sqlalchemy.orm import Session
from ..models.database import get_db
from ..models.knowledge import LearningRecordModel, QuizResultModel, ResourceFeedbackModel
from ..models.gamification import PointsModel, AchievementModel, LeaderboardModel
from ..services.gamification_service import award_points, maybe_unlock_achievement
from .auth import require_auth

router = APIRouter()


class LearningRecordRequest(BaseModel):
    student_id: str
    kp_id: str
    action: str = Field(..., max_length=64)  # watch / read / practice / review / complete
    duration: int = Field(0, ge=0, le=86400)
    progress: float = Field(0.0, ge=0.0, le=1.0)
    score: Optional[float] = Field(None, ge=0.0, le=100.0)
    meta: Dict[str, Any] = {}


class QuizResultRequest(BaseModel):
    student_id: str
    kp_id: str
    total_questions: int = Field(..., ge=1, le=100)
    correct_count: int = Field(..., ge=0, le=100)
    score: float = Field(..., ge=0.0, le=100.0)
    weak_tags: List[str] = []
    time_spent: int = Field(0, ge=0, le=7200)
    answers: List[Dict[str, Any]] = []


def _generate_id(prefix: str) -> str:
    """生成带时间戳和随机熵的 ID，降低并发冲突概率"""
    return f"{prefix}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}_{secrets.token_hex(4)}"


@router.post("/record")
async def record_learning(request: LearningRecordRequest, db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    """上报学习记录"""
    if request.student_id != _current:
        raise HTTPException(status_code=403, detail="Cannot modify other student's data")
    record_id = _generate_id("lr")
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

    # ---------- 自动积分（同一事务） ----------
    awarded = 0
    if request.action == "complete" or request.progress >= 1.0:
        awarded += 10
        maybe_unlock_achievement(
            db, request.student_id, "first_complete", "初次完成",
            "首次完成一个知识点的学习，继续保持！", "check-circle"
        )
    elif request.action == "practice":
        awarded += 5
    elif request.action in ("read", "watch", "review"):
        awarded += max(1, request.duration // 300)  # 每5分钟1分

    total = None
    if awarded > 0:
        total = award_points(db, request.student_id, awarded, f"action:{request.action}")

    db.commit()
    db.refresh(record)

    if awarded > 0:
        return {"status": "success", "record_id": record_id, "points_awarded": awarded, "total_points": total}
    return {"status": "success", "record_id": record_id}


@router.post("/quiz")
async def record_quiz(request: QuizResultRequest, db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    """上报测验结果"""
    if request.student_id != _current:
        raise HTTPException(status_code=403, detail="Cannot modify other student's data")
    quiz_id = _generate_id("qz")
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

    # ---------- 自动积分（同一事务） ----------
    awarded = int(request.score * 2)  # 满分200分
    total = None
    if awarded > 0:
        total = award_points(db, request.student_id, awarded, "quiz")
        maybe_unlock_achievement(
            db, request.student_id, "first_quiz", "初次测验",
            "完成了第一次测验，继续挑战更高分数！", "file-done"
        )
        if request.score >= 100:
            maybe_unlock_achievement(
                db, request.student_id, "perfect_score", "满分成就",
                "在一次测验中获得了满分，太棒了！", "star"
            )

    db.commit()
    db.refresh(quiz)

    if awarded > 0:
        return {"status": "success", "quiz_id": quiz_id, "points_awarded": awarded, "total_points": total}
    return {"status": "success", "quiz_id": quiz_id}


@router.get("/{student_id}/history")
async def get_learning_history(student_id: str, limit: int = Query(50, ge=1, le=200), db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    """获取学生学习历史"""
    if student_id != _current:
        raise HTTPException(status_code=403, detail="Cannot view other student's data")
    limit = min(max(limit, 1), 200)
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


@router.get("/{student_id}/completed")
async def get_completed_kps(student_id: str, db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    """
    返回该学生已标记完成的所有 kp_id（去重）。
    供前端 ResourceDetail / LearningPath 在加载时同步完成状态。
    """
    if student_id != _current:
        raise HTTPException(status_code=403, detail="Cannot view other student's data")
    rows = (
        db.query(LearningRecordModel.kp_id)
        .filter(
            LearningRecordModel.student_id == student_id,
            LearningRecordModel.progress >= 1.0,
        )
        .distinct()
        .all()
    )
    kp_ids = [r[0] for r in rows if r[0]]
    return {
        "status": "success",
        "student_id": student_id,
        "completed_kps": kp_ids,
        "count": len(kp_ids),
    }


class ResourceFeedbackRequest(BaseModel):
    student_id: str
    kp_id: str
    rating: str  # "good" / "bad"


@router.post("/feedback")
async def submit_feedback(request: ResourceFeedbackRequest, db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    """提交资源反馈（点赞/踩），同一学生对同一知识点只保留最新一条"""
    if request.student_id != _current:
        raise HTTPException(status_code=403, detail="Cannot modify other student's data")
    if request.rating not in ("good", "bad"):
        raise HTTPException(status_code=400, detail="rating must be 'good' or 'bad'")
    existing = db.query(ResourceFeedbackModel).filter(
        ResourceFeedbackModel.student_id == request.student_id,
        ResourceFeedbackModel.kp_id == request.kp_id,
    ).first()
    if existing:
        existing.rating = request.rating
    else:
        db.add(ResourceFeedbackModel(
            student_id=request.student_id,
            kp_id=request.kp_id,
            rating=request.rating,
        ))
    db.commit()
    return {"status": "success"}
