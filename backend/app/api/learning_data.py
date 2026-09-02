"""
学习数据上报API
- 学习记录、测验结果、进度
"""
import secrets

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime, timezone

from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models.database import get_db
from ..models.knowledge import LearningRecordModel, QuizResultModel, ResourceFeedbackModel
from ..models.student import StudentProfileModel
from ..models.gamification import PointsModel, AchievementModel, LeaderboardModel
from ..models.experiment import (
    ExperimentLogModel,
    ExperimentBatchModel,
    ExperimentAssignmentModel,
)
from ..services.gamification_service import award_points, maybe_unlock_achievement
from ..services.path_adjustment_engine import maybe_check_path_adjustment
from ..core.logger import setup_logger
from .auth import require_auth

router = APIRouter()
logger = setup_logger()


class LearningRecordRequest(BaseModel):
    student_id: str
    kp_id: str
    action: Literal["watch", "read", "practice", "review", "complete"] = Field(...)
    duration: int = Field(0, ge=0, le=86400)
    progress: float = Field(0.0, ge=0.0, le=1.0)
    score: Optional[float] = Field(None, ge=0.0, le=100.0)
    meta: Dict[str, Any] = {}


class ExperimentLogRequest(BaseModel):
    student_id: str
    experiment_id: Optional[str] = Field(None, max_length=64)
    experiment_type: Literal["circuit_simulate", "circuit_fault", "stm32_simulate"]
    action: Literal["run", "diagnose", "submit", "complete"] = "run"
    detail: Dict[str, Any] = {}
    duration: int = Field(0, ge=0, le=86400)


class QuizResultRequest(BaseModel):
    student_id: str
    kp_id: str
    total_questions: int = Field(..., ge=1, le=100)
    correct_count: int = Field(..., ge=0, le=100)
    score: float = Field(..., ge=0.0, le=100.0)
    weak_tags: List[str] = []
    time_spent: int = Field(0, ge=0, le=7200)
    answers: List[Dict[str, Any]] = []
    experiment_id: Optional[str] = None
    assessment_phase: Optional[str] = Field(None, pattern="^(pre|post)$")
    assessment_version: Optional[str] = Field(None, max_length=64)
    @field_validator("correct_count")
    @classmethod
    def validate_correct_count(cls, value: int, info):
        total = info.data.get("total_questions")
        if total is not None and value > total:
            raise ValueError("correct_count 不能大于 total_questions")
        return value

    @field_validator("score")
    @classmethod
    def validate_score_consistency(cls, value: float, info):
        total = info.data.get("total_questions")
        correct = info.data.get("correct_count")
        if total and correct is not None and abs(value - (correct / total * 100)) > 0.01:
            raise ValueError("score 必须与答对题数一致")
        return value

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
    if request.experiment_id:
        if not request.assessment_phase:
            raise HTTPException(status_code=422, detail="正式测评必须指定 assessment_phase")
        batch = db.query(ExperimentBatchModel).filter(
            ExperimentBatchModel.experiment_id == request.experiment_id
        ).first()
        assignment = db.query(ExperimentAssignmentModel).filter(
            ExperimentAssignmentModel.experiment_id == request.experiment_id,
            ExperimentAssignmentModel.student_id == request.student_id,
        ).first()
        if not batch or not assignment or batch.status != "active":
            raise HTTPException(status_code=409, detail="正式实验批次或学生分组不可用")
        config = batch.config or {}
        expected_version = config.get(f"{request.assessment_phase}_assessment_version")
        if expected_version and request.assessment_version != expected_version:
            raise HTTPException(status_code=422, detail="assessment_version 与实验配置不一致")
        duplicate = db.query(QuizResultModel).filter(
            QuizResultModel.experiment_id == request.experiment_id,
            QuizResultModel.student_id == request.student_id,
            QuizResultModel.assessment_phase == request.assessment_phase,
        ).first()
        if duplicate:
            raise HTTPException(status_code=409, detail="该阶段正式测评已提交")

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
        experiment_id=request.experiment_id,
        assessment_phase=request.assessment_phase,
        assessment_version=request.assessment_version,
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

    # ---------- 更新学生画像（测验结果写回） ----------
    try:
        profile = db.query(StudentProfileModel).filter(StudentProfileModel.student_id == request.student_id).first()
        if profile:
            kb = profile.knowledge_base or {}
            if request.kp_id:
                kb[request.kp_id] = max(kb.get(request.kp_id, 0), request.score / 100.0)
            if request.weak_tags:
                weak = list(set(profile.weak_areas or []))
                for tag in (request.weak_tags or []):
                    if isinstance(tag, str) and tag not in weak:
                        weak.append(tag)
                profile.weak_areas = weak
            profile.knowledge_base = kb
            db.commit()
    except Exception:
        logger.warning(f"Failed to update profile from quiz: student_id={request.student_id}")

    # 检查是否需要调整路径
    await maybe_check_path_adjustment(request.student_id, db)

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


# ---------- 实验行为日志（AIC 试点数据分析：实验参与度） ----------

@router.post("/experiment")
async def record_experiment(
    request: ExperimentLogRequest,
    db: Session = Depends(get_db),
    _current: str = Depends(require_auth),
):
    """上报实验行为（电路仿真/故障诊断/STM32仿真）

    experiment_type: circuit_simulate / circuit_fault / stm32_simulate
    action: run（运行仿真）/ diagnose（故障诊断提交）/ complete（实验完成）
    """
    if request.student_id != _current:
        raise HTTPException(status_code=403, detail="Cannot modify other student's data")
    if request.experiment_id:
        batch = db.query(ExperimentBatchModel).filter(
            ExperimentBatchModel.experiment_id == request.experiment_id
        ).first()
        assignment = db.query(ExperimentAssignmentModel).filter(
            ExperimentAssignmentModel.experiment_id == request.experiment_id,
            ExperimentAssignmentModel.student_id == request.student_id,
        ).first()
        if not batch or not assignment or batch.status != "active":
            raise HTTPException(status_code=409, detail="正式实验批次或学生分组不可用")
    db.add(ExperimentLogModel(
        student_id=request.student_id,
        experiment_id=request.experiment_id,
        experiment_type=request.experiment_type,
        action=request.action,
        detail=request.detail,
        duration=request.duration,
    ))
    db.commit()
    return {"status": "success"}


@router.get("/experiment-stats")
async def get_experiment_stats(
    student_id: Optional[str] = Query(None),
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db),
    _current: str = Depends(require_auth),
):
    """实验行为统计（试点数据分析：实验参与度）

    - 不传 student_id：全班实验参与汇总（教师权限）
    - 传 student_id：单个学生的实验参与明细（学生只能查自己）
    """
    # 权限：全班汇总或查看其他学生需教师权限
    if not student_id or student_id != _current:
        from ..models.user import UserModel
        user = db.query(UserModel).filter(UserModel.student_id == _current).first()
        if not user or user.role not in ("teacher", "admin"):
            raise HTTPException(status_code=403, detail="教师权限不足")

    from datetime import timedelta
    since = datetime.now(timezone.utc) - timedelta(days=days)
    q = db.query(
        ExperimentLogModel.experiment_type,
        ExperimentLogModel.action,
        func.count().label("count"),
    ).filter(ExperimentLogModel.created_at >= since)
    if student_id:
        q = q.filter(ExperimentLogModel.student_id == student_id)
    rows = q.group_by(
        ExperimentLogModel.experiment_type,
        ExperimentLogModel.action,
    ).all()

    # 聚合为 类型 -> {action: count}
    result: Dict[str, Any] = {}
    total = 0
    for r in rows:
        entry = result.setdefault(r.experiment_type, {"total": 0, "actions": {}})
        entry["actions"][r.action] = r.count
        entry["total"] += r.count
        total += r.count

    return {
        "status": "success",
        "days": days,
        "student_id": student_id,
        "total_experiments": total,
        "data": result,
    }
