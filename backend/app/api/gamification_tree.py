"""
游戏化成长系统 API
知识树、成长日志、挑战系统
从现有数据模型计算，不新增数据库表
"""
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func as sa_func

from ..models.database import get_db
from ..models.knowledge import LearningRecordModel, QuizResultModel, KnowledgePointModel
from ..models.gamification import PointsModel, AchievementModel
from ..models.student import StudentProfileModel
from ..models.trend import TrendDataModel

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


def _safe_float(v, default=0.0):
    try:
        return float(v) if v is not None else default
    except (ValueError, TypeError):
        return default


@router.get("/{student_id}/tree")
def get_knowledge_tree(student_id: str, db: Session = Depends(get_db)):
    """获取知识树状态 —— 从现有数据实时计算"""

    # 1. 学习记录统计
    records = db.query(LearningRecordModel).filter(
        LearningRecordModel.student_id == student_id
    ).all()

    total_records = len(records)
    completed_kps = set()
    touched_kps = set()
    total_duration = 0
    for r in records:
        touched_kps.add(r.kp_id)
        total_duration += r.duration or 0
        if r.action == "complete" or _safe_float(r.progress) >= 1.0:
            completed_kps.add(r.kp_id)

    # 2. 测验统计
    quizzes = db.query(QuizResultModel).filter(
        QuizResultModel.student_id == student_id
    ).all()
    avg_score = sum(q.score or 0 for q in quizzes) / max(len(quizzes), 1)
    total_quizzes = len(quizzes)

    # 3. 连续学习天数
    if records:
        dates = set()
        for r in records:
            if r.created_at:
                dates.add(r.created_at.strftime("%Y-%m-%d"))
        sorted_dates = sorted(dates, reverse=True)
        streak = 0
        today = datetime.now(timezone.utc).date()
        for i, d in enumerate(sorted_dates):
            expected = (today - timedelta(days=i)).isoformat()
            if d == expected:
                streak += 1
            else:
                break
    else:
        streak = 0

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
    trend_factor = _safe_float(trend.trend_factor) if trend else 0.0

    # 7. 计算树状态
    mastery_rate = len(completed_kps) / max(len(touched_kps), 1)
    hours = total_duration / 3600.0

    # 树状态逻辑
    if total_records == 0:
        tree_state = "seedling"       # 小树苗
        tree_label = "刚刚种下种子"
    elif mastery_rate < 0.3:
        tree_state = "growing"        # 长叶
        tree_label = "知识之树正在成长"
    elif mastery_rate < 0.7:
        tree_state = "blooming"       # 开花
        tree_label = "知识之树绽放中"
    else:
        tree_state = "fruiting"       # 结果
        tree_label = "知识之树硕果累累"

    # 连续学习加发光
    if streak >= 7:
        tree_state = "glowing"
        tree_label = f"连续学习{streak}天，光芒四射"

    # 学习停滞变黄
    if trend_factor < -0.3:
        tree_state = "wilting"
        tree_label = "学习状态需要关注"

    # 计算成长值
    growth_value = int(
        hours * 10 +
        avg_score * 0.5 +
        streak * 20 +
        achievements * 30 +
        len(completed_kps) * 15
    )

    # 8. 成长日志（最近的里程碑事件）
    growth_logs = []
    for r in records[-10:]:
        if r.action == "complete":
            kp = db.query(KnowledgePointModel).filter(
                KnowledgePointModel.kp_id == r.kp_id
            ).first()
            growth_logs.append({
                "date": r.created_at.strftime("%Y-%m-%d") if r.created_at else "",
                "type": "mastery",
                "message": f"掌握了「{kp.name if kp else r.kp_id}」",
                "icon": "trophy",
            })
    for q in quizzes[-5:]:
        if q.score and q.score >= 80:
            growth_logs.append({
                "date": q.created_at.strftime("%Y-%m-%d") if q.created_at else "",
                "type": "achievement",
                "message": f"测验得分 {q.score:.0f} 分",
                "icon": "star",
            })

    # 9. 每日成长趋势（最近7天）
    daily_trend = []
    today = datetime.now(timezone.utc).date()
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        d_str = d.isoformat()
        day_records = [r for r in records if r.created_at and r.created_at.strftime("%Y-%m-%d") == d_str]
        day_score = sum(_safe_float(r.score) for r in day_records if r.score)
        day_count = len(day_records)
        daily_trend.append({
            "date": d_str,
            "records": day_count,
            "score": round(day_score / max(day_count, 1), 1),
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
            "completed_kps": len(completed_kps),
            "touched_kps": len(touched_kps),
            "total_quizzes": total_quizzes,
            "avg_score": round(avg_score, 1),
            "achievements": achievements,
            "trend_factor": round(trend_factor, 3),
            "growth_logs": sorted(growth_logs, key=lambda x: x["date"], reverse=True)[:8],
            "daily_trend": daily_trend,
        },
    }
