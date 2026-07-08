"""
作业管理API
教师布置作业、学生提交、教师批改、统计分析、代码查重
"""
import uuid
import difflib
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..core.logger import setup_logger
from ..models.database import get_db
from ..models.user import UserModel
from .auth import require_auth, require_teacher, get_current_student_id

logger = setup_logger()
router = APIRouter()

# 内存存储（比赛演示用）
_assignments: Dict[str, Dict[str, Any]] = {}
_submissions: Dict[str, Dict[str, Any]] = {}


class AssignmentCreate(BaseModel):
    title: str = Field(..., max_length=200)
    description: str = Field("", max_length=2000)
    subject: str = Field("C语言", max_length=64)
    deadline: Optional[str] = None
    max_score: int = Field(100, ge=1, le=100)
    questions: List[Dict[str, Any]] = []


class AssignmentSubmit(BaseModel):
    assignment_id: str
    answers: List[Dict[str, Any]] = []
    code: Optional[str] = None
    content: Optional[str] = None


class AssignmentGrade(BaseModel):
    submission_id: str
    score: int = Field(..., ge=0)
    feedback: str = ""
    grade: Optional[str] = None


@router.post("/create")
async def create_assignment(
    request: AssignmentCreate,
    _current: str = Depends(require_teacher),
):
    """教师布置作业"""
    assignment_id = str(uuid.uuid4())[:8]
    _assignments[assignment_id] = {
        "assignment_id": assignment_id,
        "title": request.title,
        "description": request.description,
        "subject": request.subject,
        "deadline": request.deadline,
        "max_score": request.max_score,
        "questions": request.questions,
        "created_by": _current,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "active",
        "submission_count": 0,
    }
    return {"status": "success", "assignment_id": assignment_id, "message": "作业创建成功"}


@router.get("/list")
async def list_assignments(
    db: Session = Depends(get_db),
    _current: str = Depends(get_current_student_id),
):
    """获取作业列表"""
    user = db.query(UserModel).filter(UserModel.student_id == _current).first()
    is_teacher = user and user.role in ("teacher", "admin")

    result = []
    for aid, a in _assignments.items():
        # 教师看所有，学生只看未过期的
        if not is_teacher and a.get("status") != "active":
            continue
        result.append({
            "assignment_id": aid,
            "title": a["title"],
            "description": a["description"],
            "subject": a["subject"],
            "deadline": a.get("deadline"),
            "max_score": a["max_score"],
            "questions_count": len(a.get("questions", [])),
            "created_at": a["created_at"],
            "status": a["status"],
            "submission_count": a.get("submission_count", 0),
        })
    result.sort(key=lambda x: x["created_at"], reverse=True)
    return {"status": "success", "assignments": result, "total": len(result)}


@router.get("/{assignment_id}")
async def get_assignment(
    assignment_id: str,
    _current: str = Depends(get_current_student_id),
):
    """获取作业详情"""
    a = _assignments.get(assignment_id)
    if not a:
        raise HTTPException(status_code=404, detail="作业不存在")
    return {"status": "success", "assignment": a}


@router.post("/submit")
async def submit_assignment(
    request: AssignmentSubmit,
    db: Session = Depends(get_db),
    _current: str = Depends(require_auth),
):
    """学生提交作业"""
    a = _assignments.get(request.assignment_id)
    if not a:
        raise HTTPException(status_code=404, detail="作业不存在")
    if a.get("status") != "active":
        raise HTTPException(status_code=400, detail="作业已关闭")

    submission_id = str(uuid.uuid4())[:8]

    # 计算客观题得分
    score = 0
    max_score = a.get("max_score", 100)
    questions = a.get("questions", [])
    if questions and request.answers:
        correct_count = 0
        for i, q in enumerate(questions):
            if i < len(request.answers):
                if request.answers[i].get("answer") == q.get("correct_answer"):
                    correct_count += 1
        score = round(correct_count / len(questions) * max_score) if questions else 0

    _submissions[submission_id] = {
        "submission_id": submission_id,
        "assignment_id": request.assignment_id,
        "student_id": _current,
        "answers": request.answers,
        "code": request.code,
        "content": request.content,
        "score": score,
        "max_score": max_score,
        "feedback": "",
        "grade": None,
        "status": "submitted",
        "submitted_at": datetime.now(timezone.utc).isoformat(),
        "graded_at": None,
    }
    a["submission_count"] = a.get("submission_count", 0) + 1

    return {
        "status": "success",
        "submission_id": submission_id,
        "auto_score": score,
        "message": "提交成功",
    }


@router.get("/{assignment_id}/submissions")
async def get_submissions(
    assignment_id: str,
    db: Session = Depends(get_db),
    _current: str = Depends(require_teacher),
):
    """教师查看提交列表"""
    a = _assignments.get(assignment_id)
    if not a:
        raise HTTPException(status_code=404, detail="作业不存在")

    result = []
    for sid, s in _submissions.items():
        if s["assignment_id"] == assignment_id:
            user = db.query(UserModel).filter(UserModel.student_id == s["student_id"]).first()
            result.append({
                "submission_id": sid,
                "student_id": s["student_id"],
                "username": user.username if user else s["student_id"],
                "score": s["score"],
                "max_score": s["max_score"],
                "status": s["status"],
                "submitted_at": s["submitted_at"],
                "graded_at": s.get("graded_at"),
                "feedback": s.get("feedback", ""),
            })
    result.sort(key=lambda x: x["submitted_at"], reverse=True)
    return {"status": "success", "submissions": result, "total": len(result)}


@router.post("/grade")
async def grade_submission(
    request: AssignmentGrade,
    db: Session = Depends(get_db),
    _current: str = Depends(require_teacher),
):
    """教师批改作业"""
    s = _submissions.get(request.submission_id)
    if not s:
        raise HTTPException(status_code=404, detail="提交不存在")

    # 分数不能超过满分
    max_score = s.get("max_score", 100)
    score = min(request.score, max_score)
    s["score"] = score
    s["feedback"] = request.feedback
    s["grade"] = request.grade
    s["status"] = "graded"
    s["graded_at"] = datetime.now(timezone.utc).isoformat()

    return {"status": "success", "message": "批改完成"}


@router.get("/{assignment_id}/stats")
async def get_assignment_stats(
    assignment_id: str,
    db: Session = Depends(get_db),
    _current: str = Depends(require_teacher),
):
    """作业统计"""
    a = _assignments.get(assignment_id)
    if not a:
        raise HTTPException(status_code=404, detail="作业不存在")

    submissions = [s for s in _submissions.values() if s["assignment_id"] == assignment_id]
    total_students = db.query(UserModel).filter(UserModel.role == "student").count()
    submitted_count = len(submissions)
    graded_count = sum(1 for s in submissions if s["status"] == "graded")

    scores = [s["score"] for s in submissions if s["status"] == "graded"]
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0
    max_score = max(scores) if scores else 0
    min_score = min(scores) if scores else 0

    # 分数段分布
    distribution = {"0-59": 0, "60-69": 0, "70-79": 0, "80-89": 0, "90-100": 0}
    for sc in scores:
        if sc < 60:
            distribution["0-59"] += 1
        elif sc < 70:
            distribution["60-69"] += 1
        elif sc < 80:
            distribution["70-79"] += 1
        elif sc < 90:
            distribution["80-89"] += 1
        else:
            distribution["90-100"] += 1

    return {
        "status": "success",
        "stats": {
            "assignment_id": assignment_id,
            "title": a["title"],
            "total_students": total_students,
            "submitted_count": submitted_count,
            "submission_rate": round(submitted_count / max(total_students, 1) * 100, 1),
            "graded_count": graded_count,
            "avg_score": avg_score,
            "max_score": max_score,
            "min_score": min_score,
            "distribution": distribution,
        },
    }


@router.delete("/{assignment_id}")
async def delete_assignment(
    assignment_id: str,
    _current: str = Depends(require_teacher),
):
    """删除作业"""
    if assignment_id not in _assignments:
        raise HTTPException(status_code=404, detail="作业不存在")
    del _assignments[assignment_id]
    # 同时删除相关提交
    to_delete = [sid for sid, s in _submissions.items() if s["assignment_id"] == assignment_id]
    for sid in to_delete:
        del _submissions[sid]
    return {"status": "success", "message": "作业已删除"}


@router.get("/my/{student_id}")
async def get_my_submissions(
    student_id: str,
    _current: str = Depends(get_current_student_id),
):
    """学生查看自己的提交记录"""
    if student_id != _current:
        raise HTTPException(status_code=403, detail="无权查看其他学生的提交")

    result = []
    for sid, s in _submissions.items():
        if s["student_id"] == student_id:
            a = _assignments.get(s["assignment_id"], {})
            result.append({
                "submission_id": sid,
                "assignment_id": s["assignment_id"],
                "assignment_title": a.get("title", "未知作业"),
                "score": s["score"],
                "max_score": s["max_score"],
                "status": s["status"],
                "feedback": s.get("feedback", ""),
                "submitted_at": s["submitted_at"],
            })
    result.sort(key=lambda x: x["submitted_at"], reverse=True)
    return {"status": "success", "submissions": result}


@router.get("/{assignment_id}/plagiarism")
async def plagiarism_check(
    assignment_id: str,
    threshold: float = 0.7,
    _current: str = Depends(require_teacher),
):
    """代码查重检测 —— 对比同一作业下所有提交的代码相似度"""
    a = _assignments.get(assignment_id)
    if not a:
        raise HTTPException(status_code=404, detail="作业不存在")

    # 收集有代码的提交
    code_submissions = []
    for sid, s in _submissions.items():
        if s["assignment_id"] == assignment_id and s.get("code"):
            code_submissions.append({
                "submission_id": sid,
                "student_id": s["student_id"],
                "code": s["code"],
            })

    if len(code_submissions) < 2:
        return {"status": "success", "pairs": [], "message": "提交代码不足2份，无法进行查重"}

    # 两两比较
    pairs = []
    for i in range(len(code_submissions)):
        for j in range(i + 1, len(code_submissions)):
            a_code = code_submissions[i]["code"]
            b_code = code_submissions[j]["code"]
            similarity = difflib.SequenceMatcher(None, a_code, b_code).ratio()
            if similarity >= threshold:
                pairs.append({
                    "student_a": code_submissions[i]["student_id"],
                    "student_b": code_submissions[j]["student_id"],
                    "similarity": round(similarity * 100, 1),
                })

    pairs.sort(key=lambda x: x["similarity"], reverse=True)

    return {
        "status": "success",
        "pairs": pairs,
        "total_comparisons": len(code_submissions) * (len(code_submissions) - 1) // 2,
        "suspicious_count": len(pairs),
        "threshold": threshold,
    }
