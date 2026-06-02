"""
教师端API
提供全班数据概览、学生管理、成绩分析等功能
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..core.logger import setup_logger
from ..models.database import get_db
from ..models.user import UserModel
from ..models.student import StudentProfileModel
from ..models.knowledge import LearningRecordModel, QuizResultModel
from ..models.trend import TrendDataModel
from ..models.gamification import PointsModel, AchievementModel
from ..models.log_reflection import LearningLogModel, ReflectionModel
from .auth import require_teacher

logger = setup_logger()

router = APIRouter()


@router.get("/students")
async def get_all_students(
    db: Session = Depends(get_db),
    _current: str = Depends(require_teacher)
):
    """获取所有学生列表"""
    students = db.query(UserModel).filter(UserModel.role == "student").all()
    result = []
    for s in students:
        # 获取积分
        points = db.query(PointsModel).filter(PointsModel.student_id == s.student_id).first()
        # 获取最新趋势
        trend = db.query(TrendDataModel).filter(
            TrendDataModel.student_id == s.student_id
        ).order_by(TrendDataModel.date.desc()).first()

        result.append({
            "student_id": s.student_id,
            "username": s.username,
            "email": s.email,
            "is_active": s.is_active,
            "created_at": s.created_at.isoformat() if s.created_at else None,
            "total_points": points.total_points if points else 0,
            "trend_state": trend.trend_state if trend else "unknown",
            "trend_factor": trend.trend_factor if trend else 0,
        })
    return {"status": "success", "students": result, "total": len(result)}


@router.get("/overview")
async def get_overview(
    db: Session = Depends(get_db),
    _current: str = Depends(require_teacher)
):
    """全班概览统计"""
    total_students = db.query(UserModel).filter(UserModel.role == "student").count()

    # 活跃学生（最近7天有学习记录）
    from datetime import datetime, timedelta, timezone
    week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    active_students = db.query(LearningRecordModel.student_id).filter(
        LearningRecordModel.created_at >= week_ago
    ).distinct().count()

    # 平均学时（最近7天总学习时长 / 学生数）
    total_duration = db.query(func.sum(LearningRecordModel.duration)).filter(
        LearningRecordModel.created_at >= week_ago
    ).scalar() or 0
    avg_hours = round(total_duration / 3600 / max(total_students, 1), 1)

    # 平均测验成绩
    avg_score = db.query(func.avg(QuizResultModel.score)).scalar()
    avg_score = round(avg_score, 1) if avg_score else 0

    # 总测验次数
    total_quizzes = db.query(QuizResultModel).count()

    # 总学习记录数
    total_records = db.query(LearningRecordModel).count()

    return {
        "status": "success",
        "overview": {
            "total_students": total_students,
            "active_students": active_students,
            "avg_weekly_hours": avg_hours,
            "avg_score": avg_score,
            "total_quizzes": total_quizzes,
            "total_records": total_records,
        }
    }


@router.get("/student/{student_id}/detail")
async def get_student_detail(
    student_id: str,
    db: Session = Depends(get_db),
    _current: str = Depends(require_teacher)
):
    """获取单个学生详细信息"""
    user = db.query(UserModel).filter(UserModel.student_id == student_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Student not found")

    # 画像
    profile = db.query(StudentProfileModel).filter(
        StudentProfileModel.student_id == student_id
    ).first()

    # 积分
    points = db.query(PointsModel).filter(PointsModel.student_id == student_id).first()

    # 成就数
    achievements_count = db.query(AchievementModel).filter(
        AchievementModel.student_id == student_id
    ).count()

    # 最新趋势
    trend = db.query(TrendDataModel).filter(
        TrendDataModel.student_id == student_id
    ).order_by(TrendDataModel.date.desc()).first()

    # 学习统计
    total_records = db.query(LearningRecordModel).filter(
        LearningRecordModel.student_id == student_id
    ).count()
    total_duration = db.query(func.sum(LearningRecordModel.duration)).filter(
        LearningRecordModel.student_id == student_id
    ).scalar() or 0
    completed_kps = db.query(LearningRecordModel).filter(
        LearningRecordModel.student_id == student_id,
        LearningRecordModel.action == "complete"
    ).count()

    # 测验统计
    quiz_count = db.query(QuizResultModel).filter(
        QuizResultModel.student_id == student_id
    ).count()
    quiz_avg = db.query(func.avg(QuizResultModel.score)).filter(
        QuizResultModel.student_id == student_id
    ).scalar()
    quiz_avg = round(quiz_avg, 1) if quiz_avg else 0

    return {
        "status": "success",
        "student": {
            "student_id": user.student_id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "profile": {
                "knowledge_base": profile.knowledge_base if profile else {},
                "weak_areas": profile.weak_areas if profile else [],
                "cognitive_style": profile.cognitive_style if profile else {},
                "interest_areas": profile.interest_areas if profile else [],
            } if profile else None,
            "points": {
                "total": points.total_points if points else 0,
                "daily": points.daily_points if points else 0,
                "weekly": points.weekly_points if points else 0,
            },
            "achievements_count": achievements_count,
            "trend": {
                "state": trend.trend_state if trend else "unknown",
                "factor": trend.trend_factor if trend else 0,
                "predicted_mastery_3d": trend.predicted_mastery_3d if trend else 0,
                "intervention": trend.intervention if trend else None,
            } if trend else None,
            "learning_stats": {
                "total_records": total_records,
                "total_hours": round(total_duration / 3600, 1),
                "completed_kps": completed_kps,
                "quiz_count": quiz_count,
                "quiz_avg_score": quiz_avg,
            }
        }
    }


@router.get("/student/{student_id}/progress")
async def get_student_progress(
    student_id: str,
    limit: int = 50,
    db: Session = Depends(get_db),
    _current: str = Depends(require_teacher)
):
    """获取学生学习进度"""
    records = db.query(LearningRecordModel).filter(
        LearningRecordModel.student_id == student_id
    ).order_by(LearningRecordModel.created_at.desc()).limit(limit).all()

    return {
        "status": "success",
        "student_id": student_id,
        "records": [{
            "record_id": r.record_id,
            "kp_id": r.kp_id,
            "action": r.action,
            "duration": r.duration,
            "progress": r.progress,
            "score": r.score,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        } for r in records],
        "total": len(records),
    }


@router.get("/student/{student_id}/scores")
async def get_student_scores(
    student_id: str,
    limit: int = 30,
    db: Session = Depends(get_db),
    _current: str = Depends(require_teacher)
):
    """获取学生成绩数据"""
    quizzes = db.query(QuizResultModel).filter(
        QuizResultModel.student_id == student_id
    ).order_by(QuizResultModel.created_at.desc()).limit(limit).all()

    avg_score = db.query(func.avg(QuizResultModel.score)).filter(
        QuizResultModel.student_id == student_id
    ).scalar()

    return {
        "status": "success",
        "student_id": student_id,
        "quizzes": [{
            "quiz_id": q.quiz_id,
            "kp_id": q.kp_id,
            "score": q.score,
            "correct_count": q.correct_count,
            "total_questions": q.total_questions,
            "weak_tags": q.weak_tags,
            "time_spent": q.time_spent,
            "created_at": q.created_at.isoformat() if q.created_at else None,
        } for q in quizzes],
        "avg_score": round(avg_score, 1) if avg_score else 0,
        "total": len(quizzes),
    }


@router.get("/student/{student_id}/trends")
async def get_student_trends(
    student_id: str,
    days: int = 30,
    db: Session = Depends(get_db),
    _current: str = Depends(require_teacher)
):
    """获取学生趋势分析"""
    trends = db.query(TrendDataModel).filter(
        TrendDataModel.student_id == student_id
    ).order_by(TrendDataModel.date.desc()).limit(days).all()

    return {
        "status": "success",
        "student_id": student_id,
        "trends": [{
            "date": t.date,
            "trend_factor": t.trend_factor,
            "trend_state": t.trend_state,
            "mastery_trend": t.mastery_trend,
            "speed_ratio": t.speed_ratio,
            "time_efficiency": t.time_efficiency,
            "predicted_mastery_3d": t.predicted_mastery_3d,
            "intervention": t.intervention,
        } for t in trends],
    }


@router.get("/student/{student_id}/reflections")
async def get_student_reflections(
    student_id: str,
    limit: int = 20,
    db: Session = Depends(get_db),
    _current: str = Depends(require_teacher)
):
    """获取学生反思日志"""
    reflections = db.query(ReflectionModel).filter(
        ReflectionModel.student_id == student_id
    ).order_by(ReflectionModel.created_at.desc()).limit(limit).all()

    return {
        "status": "success",
        "student_id": student_id,
        "reflections": [{
            "reflection_id": r.reflection_id,
            "date": r.date,
            "content": r.content,
            "mood": r.mood,
            "tags": r.tags,
            "ai_feedback": r.ai_feedback,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        } for r in reflections],
    }


@router.get("/ranking")
async def get_ranking(
    sort_by: str = "points",
    limit: int = 20,
    db: Session = Depends(get_db),
    _current: str = Depends(require_teacher)
):
    """学生排行榜"""
    students = db.query(UserModel).filter(UserModel.role == "student").all()
    ranking = []

    for s in students:
        sid = s.student_id
        points = db.query(PointsModel).filter(PointsModel.student_id == sid).first()
        total_duration = db.query(func.sum(LearningRecordModel.duration)).filter(
            LearningRecordModel.student_id == sid
        ).scalar() or 0
        avg_score = db.query(func.avg(QuizResultModel.score)).filter(
            QuizResultModel.student_id == sid
        ).scalar()

        ranking.append({
            "student_id": sid,
            "username": s.username,
            "total_points": points.total_points if points else 0,
            "total_hours": round(total_duration / 3600, 1),
            "avg_score": round(avg_score, 1) if avg_score else 0,
        })

    if sort_by == "points":
        ranking.sort(key=lambda x: x["total_points"], reverse=True)
    elif sort_by == "hours":
        ranking.sort(key=lambda x: x["total_hours"], reverse=True)
    elif sort_by == "score":
        ranking.sort(key=lambda x: x["avg_score"], reverse=True)

    return {
        "status": "success",
        "ranking": ranking[:limit],
        "sort_by": sort_by,
    }


@router.get("/weak-points")
async def get_weak_points(
    db: Session = Depends(get_db),
    _current: str = Depends(require_teacher)
):
    """全班薄弱知识点统计"""
    # 从测验结果中统计弱项标签
    quizzes = db.query(QuizResultModel).all()
    tag_count = {}
    for q in quizzes:
        if q.weak_tags:
            for tag in q.weak_tags:
                tag_count[tag] = tag_count.get(tag, 0) + 1

    # 排序
    sorted_tags = sorted(tag_count.items(), key=lambda x: x[1], reverse=True)

    # 从学生画像中统计薄弱领域
    profiles = db.query(StudentProfileModel).all()
    weak_area_count = {}
    for p in profiles:
        if p.weak_areas:
            for area in p.weak_areas:
                if isinstance(area, str):
                    weak_area_count[area] = weak_area_count.get(area, 0) + 1

    sorted_weak = sorted(weak_area_count.items(), key=lambda x: x[1], reverse=True)

    return {
        "status": "success",
        "weak_tags": [{"tag": t, "count": c} for t, c in sorted_tags[:20]],
        "weak_areas": [{"area": a, "count": c} for a, c in sorted_weak[:20]],
    }
