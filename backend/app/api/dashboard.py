"""
Dashboard 聚合数据 API
把多个表的数据聚合成前端 Dashboard 需要的格式
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from ..models.database import get_db
from ..models.student import StudentProfileModel
from ..models.knowledge import LearningRecordModel, QuizResultModel
from ..models.gamification import PointsModel, AchievementModel, TaskModel
from ..models.favorites import FavoriteModel
from ..models.trend import TrendDataModel
from ..algorithms.effect_evaluation import LearningEffectEvaluator
from ..algorithms.trend_analysis import MultiFactorTrendAnalyzer

router = APIRouter()


def _fmt_iso(dt):
    return dt.isoformat() if dt else None


@router.get("/{student_id}/summary")
async def get_dashboard_summary(student_id: str, db: Session = Depends(get_db)):
    """获取 Dashboard 聚合数据：今日任务、统计卡片、推荐资源、画像摘要"""

    # ---------- 画像 ----------
    profile = db.query(StudentProfileModel).filter(StudentProfileModel.student_id == student_id).first()
    weak_areas = profile.weak_areas or [] if profile else []
    cognitive_style = profile.cognitive_style or {} if profile else {}
    interest_areas = profile.interest_areas or [] if profile else []

    # ---------- 今日学习时长（秒 -> 分钟） ----------
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_records = (
        db.query(LearningRecordModel)
        .filter(LearningRecordModel.student_id == student_id, LearningRecordModel.created_at >= today_start)
        .all()
    )
    today_duration_min = sum(r.duration or 0 for r in today_records) // 60

    # ---------- 本周学习时长 ----------
    week_start = today_start - timedelta(days=today_start.weekday())
    week_records = (
        db.query(LearningRecordModel)
        .filter(LearningRecordModel.student_id == student_id, LearningRecordModel.created_at >= week_start)
        .all()
    )
    weekly_duration_h = round(sum(r.duration or 0 for r in week_records) / 3600, 1)

    # ---------- 连续打卡（简化：最近有学习记录的天数） ----------
    all_records = (
        db.query(LearningRecordModel)
        .filter(LearningRecordModel.student_id == student_id)
        .order_by(LearningRecordModel.created_at.desc())
        .all()
    )
    streak = 0
    if all_records:
        seen_days = set()
        for r in all_records:
            day = r.created_at.date() if r.created_at else None
            if day:
                seen_days.add(day)
        today = datetime.now().date()
        for i in range(365):
            d = today - timedelta(days=i)
            if d in seen_days:
                streak += 1
            else:
                break

    # ---------- 掌握知识点数（进度 >= 0.8 的去重 kp_id） ----------
    mastered_kps = set()
    for r in all_records:
        if (r.progress or 0) >= 0.8:
            mastered_kps.add(r.kp_id)

    # ---------- 成就数 ----------
    ach_count = db.query(AchievementModel).filter(AchievementModel.student_id == student_id).count()

    # ---------- 收藏数 ----------
    fav_count = db.query(FavoriteModel).filter(FavoriteModel.student_id == student_id).count()

    # ---------- 待完成任务 ----------
    tasks = (
        db.query(TaskModel)
        .filter(TaskModel.student_id == student_id, TaskModel.completed == False)
        .order_by(TaskModel.created_at.desc())
        .limit(5)
        .all()
    )
    pending_tasks = [
        {
            "task_id": t.task_id,
            "title": t.title,
            "description": t.description,
            "progress": round(t.progress or 0, 2),
            "type": t.task_type,
        }
        for t in tasks
    ]

    # ---------- 推荐资源（从收藏 + 画像兴趣推导） ----------
    favorites = (
        db.query(FavoriteModel)
        .filter(FavoriteModel.student_id == student_id)
        .order_by(FavoriteModel.created_at.desc())
        .limit(4)
        .all()
    )
    recommendations = []
    type_label_map = {
        "doc": "文章",
        "video": "视频",
        "code": "代码",
        "tool": "工具",
        "article": "文章",
    }
    for f in favorites:
        recommendations.append({
            "title": f.title,
            "type": type_label_map.get(f.resource_type, "资源"),
            "url": f.url,
        })
    # 如果收藏不足，用兴趣补
    if len(recommendations) < 4 and interest_areas:
        for area in interest_areas[: 4 - len(recommendations)]:
            recommendations.append({
                "title": f"{area} 精选资源",
                "type": "推荐",
                "url": None,
            })

    # ---------- 画像摘要 ----------
    profile_summary = {
        "knowledge_base": profile.knowledge_base or {} if profile else {},
        "cognitive_style": cognitive_style,
        "weak_areas": weak_areas,
        "interest_areas": interest_areas,
    }

    # ---------- 7 天趋势（用于图表） ----------
    seven_days_ago = today_start - timedelta(days=6)
    trend_records = (
        db.query(TrendDataModel)
        .filter(TrendDataModel.student_id == student_id, TrendDataModel.date >= seven_days_ago.strftime("%Y-%m-%d"))
        .order_by(TrendDataModel.date.asc())
        .all()
    )
    trend_data = [
        {
            "date": t.date,
            "value": round((t.trend_factor or 0.5) * 100, 1),
        }
        for t in trend_records
    ]
    # 如果没有趋势数据，用学习记录凑
    if not trend_data:
        last_7_records = (
            db.query(LearningRecordModel)
            .filter(LearningRecordModel.student_id == student_id, LearningRecordModel.created_at >= seven_days_ago)
            .all()
        )
        daily_duration = {}
        for r in last_7_records:
            d = r.created_at.strftime("%m-%d") if r.created_at else "--"
            daily_duration[d] = daily_duration.get(d, 0) + (r.duration or 0)
        trend_data = [{"date": d, "value": round(v / 60, 1)} for d, v in daily_duration.items()]

    # ---------- 算法分析 ----------
    quiz_history = [
        {
            "score": q.score,
            "total_questions": q.total_questions,
            "correct_count": q.correct_count,
            "weak_tags": q.weak_tags or [],
            "created_at": q.created_at.isoformat() if q.created_at else "",
        }
        for q in db.query(QuizResultModel).filter(QuizResultModel.student_id == student_id).order_by(QuizResultModel.created_at.asc()).all()
    ]
    learning_records_raw = [
        {
            "duration": r.duration,
            "progress": r.progress,
            "created_at": r.created_at.isoformat() if r.created_at else "",
        }
        for r in db.query(LearningRecordModel).filter(LearningRecordModel.student_id == student_id).all()
    ]
    profile_dict = {
        "learning_tempo": profile.learning_tempo or {} if profile else {},
        "knowledge_base": profile.knowledge_base or {} if profile else {},
        "weak_areas": weak_areas,
        "cognitive_style": cognitive_style,
        "learning_goals": profile.learning_goals or [] if profile else [],
    }

    effect_evaluator = LearningEffectEvaluator()
    effect_result = effect_evaluator.evaluate(
        student_id=student_id,
        quiz_history=quiz_history,
        learning_records=learning_records_raw,
        weak_areas=weak_areas,
    )

    trend_analyzer = MultiFactorTrendAnalyzer()
    trend_result = trend_analyzer.analyze(
        student_id=student_id,
        quiz_history=quiz_history,
        learning_records=learning_records_raw,
        weak_areas=weak_areas,
        profile=profile_dict,
    )

    return {
        "status": "success",
        "student_id": student_id,
        "stats": {
            "weekly_hours": weekly_duration_h,
            "streak_days": streak,
            "achievements": ach_count,
            "favorites": fav_count,
            "mastered_kps": len(mastered_kps),
            "today_duration_min": today_duration_min,
        },
        "tasks": pending_tasks,
        "recommendations": recommendations,
        "profile_summary": profile_summary,
        "trend": trend_data,
        "algorithm_analysis": {
            "effect_evaluation": effect_result,
            "trend_analysis": trend_result,
        },
    }
