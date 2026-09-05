"""
Dashboard 聚合数据 API
把多个表的数据聚合成前端 Dashboard 需要的格式
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta, timezone

from ..models.database import get_db
from ..models.student import StudentProfileModel
from ..models.knowledge import LearningRecordModel, QuizResultModel, KnowledgePointModel
from ..models.gamification import PointsModel, AchievementModel, TaskModel
from ..models.favorites import FavoriteModel
from ..models.trend import TrendDataModel
from ..algorithms.effect_evaluation import LearningEffectEvaluator
from ..services.algorithm_registry import (
    build_memory_status,
    get_irt_ability,
    get_trend_weight_learner,
)
from ..algorithms.trend_analysis import MultiFactorTrendAnalyzer
from .auth import require_auth, verify_student_ownership
from ..utils import calculate_streak

router = APIRouter()


def _fmt_iso(dt):
    return dt.isoformat() if dt else None


@router.get("/{student_id}/summary")
async def get_dashboard_summary(student_id: str, db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    """获取 Dashboard 聚合数据：今日任务、统计卡片、推荐资源、画像摘要"""
    verify_student_ownership(student_id, _current)

    # ---------- 画像 ----------
    profile = db.query(StudentProfileModel).filter(StudentProfileModel.student_id == student_id).first()
    weak_areas = profile.weak_areas or [] if profile else []
    cognitive_style = profile.cognitive_style or {} if profile else {}
    interest_areas = profile.interest_areas or [] if profile else []

    # ---------- 今日学习时长（秒 -> 分钟）—— 数据库层聚合，避免全量加载 ----------
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_duration_sec = (
        db.query(func.coalesce(func.sum(LearningRecordModel.duration), 0))
        .filter(LearningRecordModel.student_id == student_id, LearningRecordModel.created_at >= today_start)
        .scalar()
    )
    today_duration_min = (today_duration_sec or 0) // 60

    # ---------- 本周学习时长 —— 数据库层聚合 ----------
    week_start = today_start - timedelta(days=today_start.weekday())
    week_duration_sec = (
        db.query(func.coalesce(func.sum(LearningRecordModel.duration), 0))
        .filter(LearningRecordModel.student_id == student_id, LearningRecordModel.created_at >= week_start)
        .scalar()
    )
    weekly_duration_h = round((week_duration_sec or 0) / 3600, 1)

    # ---------- 累计学习时长 ----------
    total_duration_sec = (
        db.query(func.coalesce(func.sum(LearningRecordModel.duration), 0))
        .filter(LearningRecordModel.student_id == student_id)
        .scalar()
    )
    total_duration_h = round((total_duration_sec or 0) / 3600, 1)

    # ---------- 连续打卡（简化：最近有学习记录的天数）—— 只查询日期字段 ----------
    year_ago = today_start - timedelta(days=365)
    recent_days = [
        str(row[0])
        for row in db.query(func.date(LearningRecordModel.created_at))
        .filter(
            LearningRecordModel.student_id == student_id,
            LearningRecordModel.created_at >= year_ago,
        )
        .distinct()
        .all()
        if row[0]
    ]
    streak = calculate_streak(recent_days)

    # ---------- 掌握知识点数（进度 >= 0.8 的去重 kp_id）—— 数据库层去重 ----------
    mastered_kps = {
        row[0]
        for row in db.query(LearningRecordModel.kp_id)
        .filter(
            LearningRecordModel.student_id == student_id,
            LearningRecordModel.created_at >= year_ago,
            LearningRecordModel.progress >= 0.8,
        )
        .distinct()
        .all()
    }

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
        if not f.url:
            continue
        recommendations.append({
            "title": f.title,
            "type": type_label_map.get(f.resource_type, "资源"),
            "url": f.url,
        })
    # 如果收藏不足，用兴趣补
    if len(recommendations) < 4:
        content_kps = (
            db.query(KnowledgePointModel)
            .filter(
                (KnowledgePointModel.document.isnot(None))
                | (KnowledgePointModel.code_example.isnot(None))
                | (KnowledgePointModel.questions.isnot(None))
                | (KnowledgePointModel.mindmap.isnot(None))
            )
            .order_by(KnowledgePointModel.created_at.desc())
            .all()
        )
        existing_urls = {item["url"] for item in recommendations if item.get("url")}
        interest_tokens = [str(area).strip().lower() for area in interest_areas if str(area).strip()]
        for kp in content_kps:
            searchable = " ".join([kp.name or "", kp.subject or "", *(kp.tags or [])]).lower()
            if interest_tokens and not any(token in searchable for token in interest_tokens):
                continue
            url = f"/resource/{kp.kp_id}"
            if url in existing_urls:
                continue
            if kp.document:
                resource_type = "文章"
            elif kp.code_example:
                resource_type = "代码"
            elif kp.questions:
                resource_type = "练习"
            else:
                resource_type = "思维导图"
            recommendations.append({"title": kp.name, "type": resource_type, "url": url})
            existing_urls.add(url)
            if len(recommendations) >= 4:
                break

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

    # ---------- 算法分析（限制最近 90 天数据，避免全表扫描） ----------
    analyze_start = today_start - timedelta(days=90)
    quiz_history = [
        {
            "score": q.score,
            "total_questions": q.total_questions,
            "correct_count": q.correct_count,
            "weak_tags": q.weak_tags or [],
            "created_at": q.created_at.isoformat() if q.created_at else "",
        }
        for q in db.query(QuizResultModel)
        .filter(QuizResultModel.student_id == student_id, QuizResultModel.created_at >= analyze_start)
        .order_by(QuizResultModel.created_at.asc())
        .all()
    ]
    learning_records_raw = [
        {
            "duration": r.duration,
            "progress": r.progress,
            "created_at": r.created_at.isoformat() if r.created_at else "",
        }
        for r in db.query(LearningRecordModel)
        .filter(LearningRecordModel.student_id == student_id, LearningRecordModel.created_at >= analyze_start)
        .all()
    ]
    profile_dict = {
        "learning_tempo": profile.learning_tempo or {} if profile else {},
        "knowledge_base": profile.knowledge_base or {} if profile else {},
        "weak_areas": weak_areas,
        "cognitive_style": cognitive_style,
        "learning_goals": profile.learning_goals or [] if profile else [],
    }

    effect_evaluator = LearningEffectEvaluator()
    # AIC 算法增强：FSRS 记忆状态（到期复习队列 + 记忆保持预警）
    memory_status = build_memory_status(db, student_id)
    # AIC 算法增强：IRT 能力 θ（已拟合时掌握度用 Φ(θ)·100 替代加权平均分）
    effect_result = effect_evaluator.evaluate(
        student_id=student_id,
        quiz_history=quiz_history,
        learning_records=learning_records_raw,
        weak_areas=weak_areas,
        memory_status=memory_status,
        irt_ability=get_irt_ability(student_id),
    )

    trend_analyzer = MultiFactorTrendAnalyzer()
    # AIC 算法增强：已训练的掉队预警学习器（学习权重 + 预警概率），未训练自动回退
    trend_result = trend_analyzer.analyze(
        student_id=student_id,
        quiz_history=quiz_history,
        learning_records=learning_records_raw,
        weak_areas=weak_areas,
        profile=profile_dict,
        weight_learner=get_trend_weight_learner(),
    )

    return {
        "status": "success",
        "student_id": student_id,
        "stats": {
            "total_hours": total_duration_h,
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


@router.get("/{student_id}/timeline")
async def get_growth_timeline(student_id: str, db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    """获取成长时间轴数据 — 里程碑事件列表"""
    verify_student_ownership(student_id, _current)

    # 查询学习记录（最近90天）
    cutoff = datetime.now(timezone.utc) - timedelta(days=90)
    records = db.query(LearningRecordModel).filter(
        LearningRecordModel.student_id == student_id,
        LearningRecordModel.created_at >= cutoff,
    ).order_by(LearningRecordModel.created_at.desc()).all()

    # 查询测验记录
    quizzes = db.query(QuizResultModel).filter(
        QuizResultModel.student_id == student_id,
        QuizResultModel.created_at >= cutoff,
    ).order_by(QuizResultModel.created_at.desc()).all()

    # 查询成就
    achievements = db.query(AchievementModel).filter(
        AchievementModel.student_id == student_id,
    ).order_by(AchievementModel.unlocked_at.desc()).all()

    # 查询趋势数据
    trends = db.query(TrendDataModel).filter(
        TrendDataModel.student_id == student_id,
        TrendDataModel.created_at >= cutoff,
    ).order_by(TrendDataModel.created_at.desc()).all()

    milestones = []

    # 掌握知识点里程碑 —— 批量查询避免 N+1
    completed_kps = set()
    candidate_kp_ids = set()
    for r in records:
        if r.action == "complete" or (r.progress and float(r.progress) >= 1.0):
            if r.kp_id not in completed_kps:
                completed_kps.add(r.kp_id)
                candidate_kp_ids.add(r.kp_id)

    kp_name_map = {}
    if candidate_kp_ids:
        kps = db.query(KnowledgePointModel).filter(
            KnowledgePointModel.kp_id.in_(candidate_kp_ids)
        ).all()
        kp_name_map = {kp.kp_id: kp.name for kp in kps}

    emitted_mastery_kps = set()
    for r in records:
        if r.action == "complete" or (r.progress and float(r.progress) >= 1.0):
            if r.kp_id in completed_kps and r.kp_id not in emitted_mastery_kps:
                emitted_mastery_kps.add(r.kp_id)
                milestones.append({
                    "date": _fmt_iso(r.created_at),
                    "type": "mastery",
                    "title": f"掌握「{kp_name_map.get(r.kp_id, r.kp_id)}」",
                    "icon": "trophy",
                    "color": "#10b981",
                })

    # 测验高分里程碑
    for q in quizzes:
        if q.score and q.score >= 90:
            milestones.append({
                "date": _fmt_iso(q.created_at),
                "type": "achievement",
                "title": f"测验获得 {q.score:.0f} 分",
                "icon": "star",
                "color": "#f59e0b",
            })

    # 成就解锁里程碑
    for a in achievements:
        milestones.append({
            "date": _fmt_iso(a.unlocked_at),
            "type": "badge",
            "title": f"解锁成就「{a.name}」",
            "icon": "medal",
            "color": "#8b5cf6",
        })

    # 趋势预警里程碑
    for t in trends:
        if t.trend_factor and float(t.trend_factor) < -0.3:
            milestones.append({
                "date": _fmt_iso(t.created_at),
                "type": "alert",
                "title": "学习状态需要关注",
                "icon": "alert",
                "color": "#ef4444",
            })

    # 按日期排序
    milestones.sort(key=lambda x: x["date"] or "", reverse=True)

    # 每日学习曲线数据（最近30天）
    daily_curve = []
    today = datetime.now(timezone.utc).date()
    for i in range(29, -1, -1):
        d = today - timedelta(days=i)
        d_str = d.isoformat()
        day_records = [r for r in records if r.created_at and r.created_at.strftime("%Y-%m-%d") == d_str]
        day_quizzes = [q for q in quizzes if q.created_at and q.created_at.strftime("%Y-%m-%d") == d_str]
        total_min = sum((r.duration or 0) for r in day_records) / 60.0
        avg_score = sum(q.score or 0 for q in day_quizzes) / max(len(day_quizzes), 1)
        daily_curve.append({
            "date": d_str,
            "minutes": round(total_min, 1),
            "kp_count": len(set(r.kp_id for r in day_records)),
            "quiz_count": len(day_quizzes),
            "avg_score": round(avg_score, 1),
        })

    return {
        "status": "success",
        "data": {
            "milestones": milestones[:50],
            "daily_curve": daily_curve,
            "summary": {
                "total_milestones": len(milestones),
                "mastery_count": len(emitted_mastery_kps),
                "high_score_count": sum(1 for m in milestones if m["type"] == "achievement"),
                "achievement_count": len(achievements),
            },
        },
    }


@router.get("/{student_id}/active-dates")
async def get_active_dates(student_id: str, year: int = Query(None), month: int = Query(None), db: Session = Depends(get_db), _current: str = Depends(require_auth)):
    """获取学生指定月份有学习活动的日期列表（用于日历高亮）"""
    verify_student_ownership(student_id, _current)
    now = datetime.now(timezone.utc)
    y = year or now.year
    m = month or now.month
    start = datetime(y, m, 1, tzinfo=timezone.utc)
    if m == 12:
        end = datetime(y + 1, 1, 1, tzinfo=timezone.utc)
    else:
        end = datetime(y, m + 1, 1, tzinfo=timezone.utc)

    records = db.query(LearningRecordModel).filter(
        LearningRecordModel.student_id == student_id,
        LearningRecordModel.created_at >= start,
        LearningRecordModel.created_at < end,
    ).all()

    active_dates = sorted(set(
        r.created_at.strftime("%Y-%m-%d")
        for r in records if r.created_at
    ))

    return {
        "status": "success",
        "data": active_dates,
    }
