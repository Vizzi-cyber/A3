"""
学情分析数据大屏接口（AIC 算法增强）
聚合班级学习数据 + 算法预测：
  - 班级总览（学生数/平均分/通过率）
  - 知识点掌握度（各 kp 平均正确率）
  - 分数段分布
  - 趋势预测（线性回归 + 移动平均，预测未来 7 天）
  - 班级对比（多班平均分）
  - 学生 × 知识点 掌握热力图数据
"""
import math
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..models.database import get_db
from ..models.knowledge import QuizResultModel
from ..models.user import UserModel
from ..core.logger import setup_logger
from .auth import require_teacher

logger = setup_logger()
router = APIRouter()


def _linear_regression_predict(values: List[float], steps: int = 7) -> List[float]:
    """线性回归预测：y = a + b*x，外推未来 steps 天。"""
    n = len(values)
    if n < 3:
        return [round(v, 1) for v in values] + [round(float(values[-1]), 1)] * steps
    xs = list(range(n))
    mean_x = sum(xs) / n
    mean_y = sum(values) / n
    b = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, values)) / (
        sum((x - mean_x) ** 2 for x in xs) or 1
    )
    a = mean_y - b * mean_x
    return [round(a + b * (n + i), 1) for i in range(steps)]


def _moving_average(values: List[float], window: int = 3) -> List[float]:
    """移动平均平滑（用于趋势线）。"""
    if not values:
        return []
    out = []
    for i in range(len(values)):
        lo = max(0, i - window + 1)
        out.append(round(sum(values[lo:i + 1]) / (i - lo + 1), 1))
    return out


@router.get("/dashboard")
async def analytics_dashboard(
    class_id: Optional[str] = None,
    db: Session = Depends(get_db),
    _auth: str = Depends(require_teacher),
):
    """班级学情大屏聚合数据 + 趋势预测。"""
    # 学生（按班级过滤）
    stu_q = db.query(UserModel).filter(UserModel.role == "student")
    if class_id:
        stu_q = stu_q.filter(UserModel.class_id == class_id)
    students = stu_q.all()
    student_ids = {s.student_id for s in students}

    # 测验数据
    quiz_q = db.query(QuizResultModel)
    if class_id:
        quiz_q = quiz_q.filter(QuizResultModel.student_id.in_(student_ids))
    quizzes = quiz_q.all()

    if not quizzes:
        return {"status": "success", "data": {"empty": True, "message": "暂无测验数据"}}

    # 班级总览
    scores = [q.score for q in quizzes if q.score is not None]
    avg_score = sum(scores) / len(scores) if scores else 0
    pass_rate = sum(1 for s in scores if s >= 60) / len(scores) * 100 if scores else 0

    # 知识点掌握度（kp -> 平均正确率，用 score 近似或 answers 逐题）
    kp_scores: Dict[str, List[float]] = defaultdict(list)
    for q in quizzes:
        kp_scores[q.kp_id].append(q.score or 0)
    kp_mastery = [
        {"kp": kp, "mastery": round(sum(v) / len(v), 1)}
        for kp, v in sorted(kp_scores.items(), key=lambda x: -sum(x[1]) / len(x[1]))
    ][:12]

    # 分数段分布
    bins = [0, 60, 70, 80, 90, 100]
    dist = [0] * (len(bins) - 1)
    for s in scores:
        for i in range(len(bins) - 1):
            if bins[i] <= s < bins[i + 1]:
                dist[i] += 1
                break
    if scores and max(scores) == 100:
        dist[-1] += 1  # 100 分
    score_dist = [
        {"range": f"{bins[i]}-{bins[i + 1]}", "count": dist[i]}
        for i in range(len(bins) - 1)
    ]

    # 每日平均分序列（过去 14 天）+ 预测
    by_day: Dict[str, List[float]] = defaultdict(list)
    for q in quizzes:
        if q.created_at:
            day = q.created_at.date().isoformat()
            by_day[day].append(q.score or 0)
    days = sorted(by_day.keys())[-14:]
    trend = [round(sum(by_day[d]) / len(by_day[d]), 1) for d in days]
    forecast = _linear_regression_predict(trend, 7)

    # 班级对比（各班级平均分）
    class_scores: Dict[str, List[float]] = defaultdict(list)
    for q in quizzes:
        st = next((s for s in students if s.student_id == q.student_id), None)
        if st and st.class_id:
            class_scores[st.class_id].append(q.score or 0)
    class_compare = [
        {"class": c, "avg": round(sum(v) / len(v), 1), "count": len(v)}
        for c, v in sorted(class_scores.items())
    ]

    # 学生 × 知识点热力图（前 8 学生 × 前 6 知识点）
    top_students = sorted(
        {q.student_id for q in quizzes},
        key=lambda sid: -sum(q.score or 0 for q in quizzes if q.student_id == sid),
    )[:8]
    top_kps = [k["kp"] for k in kp_mastery[:6]]
    heatmap = []
    for sid in top_students:
        row = []
        for kp in top_kps:
            vals = [q.score or 0 for q in quizzes if q.student_id == sid and q.kp_id == kp]
            row.append(round(sum(vals) / len(vals), 0) if vals else None)
        heatmap.append({"student": sid, "values": row})

    return {
        "status": "success",
        "data": {
            "empty": False,
            "overview": {
                "students": len(student_ids),
                "quizzes": len(quizzes),
                "avg_score": round(avg_score, 1),
                "pass_rate": round(pass_rate, 1),
                "kps_covered": len(kp_scores),
            },
            "kp_mastery": kp_mastery,
            "score_dist": score_dist,
            "trend": {"days": days, "values": trend, "forecast": forecast, "smoothed": _moving_average(trend)},
            "class_compare": class_compare,
            "heatmap": {"students": top_students, "kps": top_kps, "data": heatmap},
        },
    }


@router.get("/prediction")
async def student_score_prediction(
    student_id: str,
    db: Session = Depends(get_db),
    _auth: str = Depends(require_teacher),
):
    """学生未来成绩预测（线性回归 + 学习趋势修正）。"""
    quizzes = (
        db.query(QuizResultModel)
        .filter(QuizResultModel.student_id == student_id)
        .order_by(QuizResultModel.created_at)
        .all()
    )
    scores = [q.score or 0 for q in quizzes]
    if len(scores) < 2:
        return {"status": "success", "data": {"prediction": round(float(scores[-1] or 60), 1), "confidence": "low"}}
    pred = _linear_regression_predict(scores, 3)
    # 置信度：数据量 + 拟合残差
    n = len(scores)
    confidence = "high" if n >= 8 else ("medium" if n >= 4 else "low")
    return {
        "status": "success",
        "data": {
            "history": scores,
            "prediction": pred,
            "next_expected": pred[0],
            "confidence": confidence,
        },
    }
