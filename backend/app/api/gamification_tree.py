"""
游戏化成长系统 API
知识树、成长日志、挑战系统
从现有数据模型计算，不新增数据库表
"""
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func as sa_func

from ..models.database import get_db
from ..models.knowledge import LearningRecordModel, QuizResultModel, KnowledgePointModel
from ..models.gamification import PointsModel, AchievementModel
from ..models.student import StudentProfileModel
from ..models.trend import TrendDataModel
from ..utils import safe_float, calculate_streak
from .auth import require_auth

router = APIRouter()

# ---------- 等级配置（统一管理，前端通过 /level-config 接口获取） ----------
XP_PER_LEVEL = 500
LEVEL_NAMES = {
    1: "初学者",
    2: "探索者",
    3: "学习者",
    4: "进阶者",
    5: "熟练者",
    6: "精通者",
    7: "专家",
    8: "大师",
    9: "宗师",
    10: "传奇",
}
MAX_LEVEL = max(LEVEL_NAMES.keys())


def _calc_level(total_points: int) -> dict:
    """计算等级详情"""
    raw_level = total_points // XP_PER_LEVEL + 1
    level = min(raw_level, MAX_LEVEL)
    current_xp = total_points % XP_PER_LEVEL
    return {
        "level": level,
        "level_name": LEVEL_NAMES.get(level, f"Lv.{level}"),
        "current_xp": current_xp,
        "xp_to_next": XP_PER_LEVEL if level < MAX_LEVEL else 0,
        "total_xp": total_points,
        "xp_per_level": XP_PER_LEVEL,
        "progress_pct": round(current_xp / XP_PER_LEVEL * 100) if level < MAX_LEVEL else 100,
    }


@router.get("/level-config")
def get_level_config():
    """返回等级配置，供前端统一使用"""
    return {
        "status": "success",
        "data": {
            "xp_per_level": XP_PER_LEVEL,
            "max_level": MAX_LEVEL,
            "level_names": LEVEL_NAMES,
        },
    }


@router.get("/{student_id}/tree")
def get_knowledge_tree(student_id: str, db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    """获取知识树状态 —— 从现有数据实时计算（SQL 聚合，避免全量加载）"""
    if student_id != _current:
        raise HTTPException(status_code=403, detail="Cannot view other student's tree")

    # 1. 学习记录统计（SQL 聚合）
    stats = db.query(
        sa_func.count(LearningRecordModel.record_id).label("total_records"),
        sa_func.coalesce(sa_func.sum(LearningRecordModel.duration), 0).label("total_duration"),
        sa_func.count(sa_func.distinct(LearningRecordModel.kp_id)).label("touched_kps"),
    ).filter(LearningRecordModel.student_id == student_id).first()

    total_records = stats.total_records or 0
    total_duration = stats.total_duration or 0
    touched_kps_count = stats.touched_kps or 0

    # 已完成的知识点（progress >= 1.0 或 action == "complete"）
    completed_kps_rows = (
        db.query(sa_func.distinct(LearningRecordModel.kp_id))
        .filter(
            LearningRecordModel.student_id == student_id,
            (LearningRecordModel.action == "complete") | (LearningRecordModel.progress >= 1.0),
        )
        .all()
    )
    completed_kps_count = len(completed_kps_rows)

    # 2. 测验统计（SQL 聚合）
    quiz_stats = db.query(
        sa_func.count(QuizResultModel.quiz_id).label("total_quizzes"),
        sa_func.coalesce(sa_func.avg(QuizResultModel.score), 0).label("avg_score"),
    ).filter(QuizResultModel.student_id == student_id).first()
    total_quizzes = quiz_stats.total_quizzes or 0
    avg_score = float(quiz_stats.avg_score or 0)

    # 3. 连续学习天数（只查询日期字段）
    year_ago = datetime.now(timezone.utc) - timedelta(days=365)
    date_rows = (
        db.query(sa_func.date(LearningRecordModel.created_at).label("day"))
        .filter(
            LearningRecordModel.student_id == student_id,
            LearningRecordModel.created_at >= year_ago,
        )
        .distinct()
        .all()
    )
    dates = [str(r[0]) for r in date_rows if r[0]]
    streak = calculate_streak(dates)

    # 4. 积分和等级
    points = db.query(PointsModel).filter(
        PointsModel.student_id == student_id
    ).first()
    total_points = points.total_points if points else 0
    level_info = _calc_level(total_points)
    level = level_info["level"]

    # 5. 成就数
    achievements = db.query(AchievementModel).filter(
        AchievementModel.student_id == student_id
    ).count()

    # 6. 趋势数据
    trend = db.query(TrendDataModel).filter(
        TrendDataModel.student_id == student_id
    ).order_by(TrendDataModel.created_at.desc()).first()
    trend_factor = safe_float(trend.trend_factor) if trend else 0.0

    # 7. 计算树状态
    mastery_rate = completed_kps_count / max(touched_kps_count, 1)
    hours = total_duration / 3600.0

    if total_records == 0:
        tree_state = "seedling"
        tree_label = "刚刚种下种子"
    elif mastery_rate < 0.3:
        tree_state = "growing"
        tree_label = "知识之树正在成长"
    elif mastery_rate < 0.7:
        tree_state = "blooming"
        tree_label = "知识之树绽放中"
    else:
        tree_state = "fruiting"
        tree_label = "知识之树硕果累累"

    if streak >= 7:
        tree_state = "glowing"
        tree_label = f"连续学习{streak}天，光芒四射"

    if trend_factor < -0.3:
        tree_state = "wilting"
        tree_label = "学习状态需要关注"

    growth_value = int(
        hours * 10 +
        avg_score * 0.5 +
        streak * 20 +
        achievements * 30 +
        completed_kps_count * 15
    )

    # 8. 成长日志（批量查询避免 N+1）
    recent_complete = (
        db.query(LearningRecordModel)
        .filter(
            LearningRecordModel.student_id == student_id,
            LearningRecordModel.action == "complete",
        )
        .order_by(LearningRecordModel.created_at.desc())
        .limit(10)
        .all()
    )
    kp_ids = [r.kp_id for r in recent_complete if r.kp_id]
    kp_name_map = {}
    if kp_ids:
        kps = db.query(KnowledgePointModel).filter(KnowledgePointModel.kp_id.in_(kp_ids)).all()
        kp_name_map = {kp.kp_id: kp.name for kp in kps}

    growth_logs = []
    for r in recent_complete:
        growth_logs.append({
            "date": r.created_at.strftime("%Y-%m-%d") if r.created_at else "",
            "type": "mastery",
            "message": f"掌握了「{kp_name_map.get(r.kp_id, r.kp_id)}」",
            "icon": "trophy",
        })

    recent_high_quiz = (
        db.query(QuizResultModel)
        .filter(
            QuizResultModel.student_id == student_id,
            QuizResultModel.score >= 80,
        )
        .order_by(QuizResultModel.created_at.desc())
        .limit(5)
        .all()
    )
    for q in recent_high_quiz:
        growth_logs.append({
            "date": q.created_at.strftime("%Y-%m-%d") if q.created_at else "",
            "type": "achievement",
            "message": f"测验得分 {q.score:.0f} 分",
            "icon": "star",
        })

    # 9. 每日成长趋势（SQL 聚合，最近7天）
    seven_days_ago = datetime.now(timezone.utc).date() - timedelta(days=6)
    daily_rows = (
        db.query(
            sa_func.date(LearningRecordModel.created_at).label("day"),
            sa_func.count(LearningRecordModel.record_id).label("cnt"),
            sa_func.coalesce(sa_func.sum(LearningRecordModel.score), 0).label("total_score"),
        )
        .filter(
            LearningRecordModel.student_id == student_id,
            LearningRecordModel.created_at >= datetime.combine(seven_days_ago, datetime.min.time()).replace(tzinfo=timezone.utc),
        )
        .group_by(sa_func.date(LearningRecordModel.created_at))
        .all()
    )
    daily_map = {str(r.day): (r.cnt, float(r.total_score or 0)) for r in daily_rows}

    daily_trend = []
    today = datetime.now(timezone.utc).date()
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        d_str = d.isoformat()
        cnt, total_score = daily_map.get(d_str, (0, 0.0))
        daily_trend.append({
            "date": d_str,
            "records": cnt,
            "score": round(total_score / max(cnt, 1), 1),
        })

    return {
        "status": "success",
        "data": {
            "tree_state": tree_state,
            "tree_label": tree_label,
            "growth_value": growth_value,
            "level": level,
            "level_name": level_info["level_name"],
            "level_info": level_info,
            "total_points": total_points,
            "streak_days": streak,
            "mastery_rate": round(mastery_rate * 100, 1),
            "total_hours": round(hours, 1),
            "completed_kps": completed_kps_count,
            "touched_kps": touched_kps_count,
            "total_quizzes": total_quizzes,
            "avg_score": round(avg_score, 1),
            "achievements": achievements,
            "trend_factor": round(trend_factor, 3),
            "growth_logs": sorted(growth_logs, key=lambda x: x["date"], reverse=True)[:8],
            "daily_trend": daily_trend,
        },
    }
