"""正式教学实验管理与效果报告 API。"""
from datetime import datetime, timezone
import hashlib
import math
import random
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..models.database import get_db
from ..models.experiment import (
    ExperimentAssignmentModel,
    ExperimentBatchModel,
    ExperimentFeedbackModel,
)
from ..models.knowledge import QuizResultModel
from .auth import require_auth, require_teacher

router = APIRouter()


class ExperimentCreateRequest(BaseModel):
    experiment_id: str = Field(..., min_length=1, max_length=64)
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    intervention_type: str = Field("ai_learning_path", max_length=64)
    seed: Optional[int] = None
    config: Dict[str, Any] = {}


class AssignmentRequest(BaseModel):
    student_ids: List[str] = Field(..., min_length=2)
    seed: Optional[int] = None


class FeedbackRequest(BaseModel):
    experiment_id: str
    questionnaire_version: str = Field(..., min_length=1, max_length=64)
    answers: Dict[str, Any] = {}
    comment: Optional[str] = Field(None, max_length=2000)


def _get_batch(db: Session, experiment_id: str) -> ExperimentBatchModel:
    batch = db.query(ExperimentBatchModel).filter(
        ExperimentBatchModel.experiment_id == experiment_id
    ).first()
    if not batch:
        raise HTTPException(status_code=404, detail="实验批次不存在")
    return batch


def _assignment_payload(assignment: ExperimentAssignmentModel) -> Dict[str, Any]:
    return {
        "experiment_id": assignment.experiment_id,
        "student_id": assignment.student_id,
        "group_name": assignment.group_name,
        "allocation_method": assignment.allocation_method,
        "allocation_seed": assignment.allocation_seed,
        "assigned_at": assignment.assigned_at.isoformat() if assignment.assigned_at else None,
    }


def _mean(values: List[float]) -> Optional[float]:
    return round(sum(values) / len(values), 4) if values else None


def _sample_std(values: List[float]) -> Optional[float]:
    if len(values) < 2:
        return None
    mean = sum(values) / len(values)
    return round(math.sqrt(sum((value - mean) ** 2 for value in values) / (len(values) - 1)), 4)


def _group_report(assignments: List[ExperimentAssignmentModel], quizzes: List[QuizResultModel]) -> Dict[str, Any]:
    assigned = {item.student_id for item in assignments}
    by_student: Dict[str, Dict[str, float]] = {}
    for quiz in quizzes:
        if quiz.student_id in assigned and quiz.assessment_phase in ("pre", "post"):
            by_student.setdefault(quiz.student_id, {})[quiz.assessment_phase] = float(quiz.score or 0)
    paired = [values["post"] - values["pre"] for values in by_student.values() if "pre" in values and "post" in values]
    pre = [values["pre"] for values in by_student.values() if "pre" in values]
    post = [values["post"] for values in by_student.values() if "post" in values]
    return {
        "n_assigned": len(assignments),
        "n_pre": len(pre),
        "n_post": len(post),
        "n_paired": len(paired),
        "pre_mean": _mean(pre),
        "post_mean": _mean(post),
        "improvement_mean": _mean(paired),
        "improvement_std": _sample_std(paired),
    }


def _welch_t(group_a: List[float], group_b: List[float]) -> Optional[Dict[str, float]]:
    if len(group_a) < 2 or len(group_b) < 2:
        return None
    mean_a, mean_b = sum(group_a) / len(group_a), sum(group_b) / len(group_b)
    var_a = sum((x - mean_a) ** 2 for x in group_a) / (len(group_a) - 1)
    var_b = sum((x - mean_b) ** 2 for x in group_b) / (len(group_b) - 1)
    standard_error = math.sqrt(var_a / len(group_a) + var_b / len(group_b))
    if standard_error == 0:
        return {"t_stat": 0.0, "p_value": 1.0}
    t_stat = (mean_a - mean_b) / standard_error
    return {"t_stat": round(t_stat, 4), "p_value": None}


@router.post("")
async def create_experiment(request: ExperimentCreateRequest, db: Session = Depends(get_db), _current: str = Depends(require_teacher)):
    if db.query(ExperimentBatchModel).filter(ExperimentBatchModel.experiment_id == request.experiment_id).first():
        raise HTTPException(status_code=409, detail="实验批次 ID 已存在")
    batch = ExperimentBatchModel(
        experiment_id=request.experiment_id,
        name=request.name,
        description=request.description,
        intervention_type=request.intervention_type,
        seed=request.seed,
        config=request.config,
        created_by=_current,
    )
    db.add(batch)
    db.commit()
    db.refresh(batch)
    return {"status": "success", "experiment": {"experiment_id": batch.experiment_id, "name": batch.name, "status": batch.status}}


@router.get("")
async def list_experiments(db: Session = Depends(get_db), _current: str = Depends(require_teacher)):
    batches = db.query(ExperimentBatchModel).order_by(ExperimentBatchModel.created_at.desc()).all()
    return {"status": "success", "experiments": [
        {"experiment_id": b.experiment_id, "name": b.name, "status": b.status, "intervention_type": b.intervention_type, "seed": b.seed}
        for b in batches
    ]}


@router.post("/{experiment_id}/assign")
async def assign_students(experiment_id: str, request: AssignmentRequest, db: Session = Depends(get_db), _current: str = Depends(require_teacher)):
    batch = _get_batch(db, experiment_id)
    if batch.status != "draft":
        raise HTTPException(status_code=409, detail="实验批次已锁定，不能重新分组")
    if len(set(request.student_ids)) != len(request.student_ids):
        raise HTTPException(status_code=422, detail="student_ids 不能重复")
    seed = request.seed if request.seed is not None else (batch.seed if batch.seed is not None else 0)
    rng = random.Random(seed)
    student_ids = list(request.student_ids)
    rng.shuffle(student_ids)
    half = len(student_ids) // 2
    if half == 0 or len(student_ids) - half == 0:
        raise HTTPException(status_code=422, detail="至少需要两名学生")
    db.query(ExperimentAssignmentModel).filter(ExperimentAssignmentModel.experiment_id == experiment_id).delete()
    assignments = []
    for index, student_id in enumerate(student_ids):
        group = "experiment" if index < half else "control"
        assignment = ExperimentAssignmentModel(
            experiment_id=experiment_id,
            student_id=student_id,
            group_name=group,
            allocation_method="seeded_random",
            allocation_seed=seed,
        )
        db.add(assignment)
        assignments.append(assignment)
    db.commit()
    return {"status": "success", "assignments": [_assignment_payload(item) for item in assignments]}


@router.post("/{experiment_id}/activate")
async def activate_experiment(experiment_id: str, db: Session = Depends(get_db), _current: str = Depends(require_teacher)):
    batch = _get_batch(db, experiment_id)
    assignments = db.query(ExperimentAssignmentModel).filter(ExperimentAssignmentModel.experiment_id == experiment_id).all()
    if batch.status != "draft" or not assignments:
        raise HTTPException(status_code=409, detail="批次必须处于 draft 且已完成分组")
    batch.status = "active"
    db.commit()
    return {"status": "success", "experiment_id": experiment_id, "state": batch.status}


@router.post("/{experiment_id}/complete")
async def complete_experiment(experiment_id: str, db: Session = Depends(get_db), _current: str = Depends(require_teacher)):
    batch = _get_batch(db, experiment_id)
    if batch.status != "active":
        raise HTTPException(status_code=409, detail="只有 active 批次可以完成")
    batch.status = "completed"
    db.commit()
    return {"status": "success", "experiment_id": experiment_id, "state": batch.status}


@router.get("/{experiment_id}/assignment")
async def get_my_assignment(experiment_id: str, db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    assignment = db.query(ExperimentAssignmentModel).filter(
        ExperimentAssignmentModel.experiment_id == experiment_id,
        ExperimentAssignmentModel.student_id == _current,
    ).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="未找到实验分组")
    return {"status": "success", "assignment": _assignment_payload(assignment)}


@router.post("/{experiment_id}/feedback")
async def submit_feedback(experiment_id: str, request: FeedbackRequest, db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    if request.experiment_id != experiment_id:
        raise HTTPException(status_code=422, detail="experiment_id 不一致")
    batch = _get_batch(db, experiment_id)
    if batch.status not in ("active", "completed"):
        raise HTTPException(status_code=409, detail="当前批次不接受问卷")
    assignment = db.query(ExperimentAssignmentModel).filter(
        ExperimentAssignmentModel.experiment_id == experiment_id,
        ExperimentAssignmentModel.student_id == _current,
    ).first()
    if not assignment:
        raise HTTPException(status_code=403, detail="不属于该实验批次")
    feedback = db.query(ExperimentFeedbackModel).filter(
        ExperimentFeedbackModel.experiment_id == experiment_id,
        ExperimentFeedbackModel.student_id == _current,
        ExperimentFeedbackModel.questionnaire_version == request.questionnaire_version,
    ).first()
    if feedback:
        feedback.answers = request.answers
        feedback.comment = request.comment
        feedback.submitted_at = datetime.now(timezone.utc)
    else:
        feedback = ExperimentFeedbackModel(
            experiment_id=experiment_id,
            student_id=_current,
            questionnaire_version=request.questionnaire_version,
            answers=request.answers,
            comment=request.comment,
        )
        db.add(feedback)
    db.commit()
    return {"status": "success", "feedback_id": feedback.id}


@router.get("/{experiment_id}/report")
async def experiment_report(experiment_id: str, db: Session = Depends(get_db), _current: str = Depends(require_teacher)):
    batch = _get_batch(db, experiment_id)
    assignments = db.query(ExperimentAssignmentModel).filter(ExperimentAssignmentModel.experiment_id == experiment_id).all()
    quizzes = db.query(QuizResultModel).filter(
        QuizResultModel.experiment_id == experiment_id,
        QuizResultModel.assessment_phase.in_(["pre", "post"]),
    ).all()
    groups = {}
    improvement_values = {}
    for group_name in ("experiment", "control"):
        group_assignments = [a for a in assignments if a.group_name == group_name]
        groups[group_name] = _group_report(group_assignments, quizzes)
        student_ids = {a.student_id for a in group_assignments}
        scores: Dict[str, Dict[str, float]] = {}
        for quiz in quizzes:
            if quiz.student_id in student_ids:
                scores.setdefault(quiz.student_id, {})[quiz.assessment_phase] = float(quiz.score or 0)
        improvement_values[group_name] = [v["post"] - v["pre"] for v in scores.values() if "pre" in v and "post" in v]
    exp, ctl = improvement_values["experiment"], improvement_values["control"]
    difference = (_mean(exp) - _mean(ctl)) if exp and ctl else None
    minimum = int((batch.config or {}).get("minimum_paired_samples", 5))
    sufficient = len(exp) >= minimum and len(ctl) >= minimum
    return {
        "status": "success" if sufficient else "insufficient_data",
        "experiment_id": experiment_id,
        "batch_status": batch.status,
        "groups": groups,
        "effect": {"improvement_difference": round(difference, 4) if difference is not None else None, "welch_t": _welch_t(exp, ctl) if sufficient else None},
        "feedback_count": db.query(ExperimentFeedbackModel).filter(ExperimentFeedbackModel.experiment_id == experiment_id).count(),
        "message": None if sufficient else f"两组配对样本均需至少 {minimum} 条",
    }


@router.get("/{experiment_id}/feedback-summary")
async def feedback_summary(experiment_id: str, db: Session = Depends(get_db), _current: str = Depends(require_teacher)):
    _get_batch(db, experiment_id)
    rows = db.query(ExperimentFeedbackModel).filter(ExperimentFeedbackModel.experiment_id == experiment_id).all()
    return {"status": "success", "experiment_id": experiment_id, "count": len(rows), "responses": [
        {"student_id": row.student_id, "questionnaire_version": row.questionnaire_version, "answers": row.answers, "comment": row.comment}
        for row in rows
    ]}
