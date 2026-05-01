"""
学习数据上报API
- 学习记录、测验结果、进度
"""
import secrets

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from sqlalchemy.orm import Session
from ..models.database import get_db
from ..models.knowledge import LearningRecordModel, QuizResultModel
from ..models.gamification import PointsModel, AchievementModel
from .auth import require_auth

router = APIRouter()


def _ensure_points(db: Session, student_id: str) -> PointsModel:
    points = db.query(PointsModel).filter(PointsModel.student_id == student_id).first()
    if not points:
        points = PointsModel(student_id=student_id, total_points=0, daily_points=0, weekly_points=0)
        db.add(points)
        db.flush()
    return points


def _award_points(db: Session, student_id: str, amount: int, reason: str = "") -> int:
    """在同一事务中 awarding points（调用方负责 commit）"""
    points = _ensure_points(db, student_id)
    points.total_points += amount
    points.daily_points += amount
    points.weekly_points += amount
    return points.total_points


def _maybe_unlock_achievement(db: Session, student_id: str, achievement_id: str, name: str, description: str, icon: str = "trophy"):
    """在同一事务中解锁成就（调用方负责 commit）"""
    existing = db.query(AchievementModel).filter(
        AchievementModel.student_id == student_id,
        AchievementModel.achievement_id == achievement_id,
    ).first()
    if existing:
        return
    ach = AchievementModel(
        student_id=student_id,
        achievement_id=achievement_id,
        name=name,
        description=description,
        icon=icon,
    )
    db.add(ach)


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


def _generate_id(prefix: str) -> str:
    """生成带时间戳和随机熵的 ID，降低并发冲突概率"""
    return f"{prefix}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}_{secrets.token_hex(4)}"


@router.post("/record")
async def record_learning(request: LearningRecordRequest, db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    """上报学习记录"""
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
        _maybe_unlock_achievement(
            db, request.student_id, "first_complete", "初次完成",
            "首次完成一个知识点的学习，继续保持！", "check-circle"
        )
    elif request.action == "practice":
        awarded += 5
    elif request.action in ("read", "watch", "review"):
        awarded += max(1, request.duration // 300)  # 每5分钟1分

    total = None
    if awarded > 0:
        total = _award_points(db, request.student_id, awarded, f"action:{request.action}")

    db.commit()
    db.refresh(record)

    if awarded > 0:
        return {"status": "success", "record_id": record_id, "points_awarded": awarded, "total_points": total}
    return {"status": "success", "record_id": record_id}


@router.post("/quiz")
async def record_quiz(request: QuizResultRequest, db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    """上报测验结果"""
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
        total = _award_points(db, request.student_id, awarded, "quiz")
        _maybe_unlock_achievement(
            db, request.student_id, "first_quiz", "初次测验",
            "完成了第一次测验，继续挑战更高分数！", "file-done"
        )
        if request.score >= 100:
            _maybe_unlock_achievement(
                db, request.student_id, "perfect_score", "满分成就",
                "在一次测验中获得了满分，太棒了！", "star"
            )

    db.commit()
    db.refresh(quiz)

    if awarded > 0:
        return {"status": "success", "quiz_id": quiz_id, "points_awarded": awarded, "total_points": total}
    return {"status": "success", "quiz_id": quiz_id}


@router.get("/{student_id}/history")
async def get_learning_history(student_id: str, limit: int = 50, db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    """获取学生学习历史"""
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
    rows = (
        db.query(LearningRecordModel.kp_id)
        .filter(
            LearningRecordModel.student_id == student_id,
            LearningRecordModel.action == "complete",
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
