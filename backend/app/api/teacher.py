"""
教师端API
提供全班数据概览、学生管理、成绩分析等功能
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from collections import defaultdict
from datetime import datetime, timedelta, timezone
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
    if not students:
        return {"status": "success", "students": [], "total": 0}
    student_ids = [s.student_id for s in students]
    points_by_student = dict(
        db.query(PointsModel.student_id, func.max(PointsModel.total_points))
        .filter(PointsModel.student_id.in_(student_ids))
        .group_by(PointsModel.student_id)
        .all()
    )
    latest_trend_date = (
        db.query(
            TrendDataModel.student_id,
            func.max(TrendDataModel.date).label("latest_date"),
        )
        .filter(TrendDataModel.student_id.in_(student_ids))
        .group_by(TrendDataModel.student_id)
        .subquery()
    )
    latest_trends = {
        row.student_id: row
        for row in db.query(TrendDataModel)
        .join(
            latest_trend_date,
            (TrendDataModel.student_id == latest_trend_date.c.student_id)
            & (TrendDataModel.date == latest_trend_date.c.latest_date),
        )
        .all()
    }
    result = []
    for s in students:
        trend = latest_trends.get(s.student_id)
        result.append({
            "student_id": s.student_id,
            "username": s.username,
            "email": s.email,
            "is_active": s.is_active,
            "class_id": s.class_id,
            "created_at": s.created_at.isoformat() if s.created_at else None,
            "total_points": points_by_student.get(s.student_id, 0),
            "trend_state": trend.trend_state if trend else "unknown",
            "trend_factor": trend.trend_factor if trend else 0,
        })
    return {"status": "success", "students": result, "total": len(result)}


@router.get("/classes")
async def get_classes(db: Session = Depends(get_db), _current: str = Depends(require_teacher)):
    """班级列表（含人数，试点分组/班级对比）"""
    from ..models.knowledge import LearningRecordModel, QuizResultModel

    rows = db.query(
        UserModel.class_id,
        func.count(UserModel.student_id).label("student_count"),
    ).filter(
        UserModel.role == "student",
        UserModel.class_id.isnot(None),
    ).group_by(UserModel.class_id).all()

    classes = []
    for r in rows:
        # 班级聚合：平均分/平均积分/平均学习时长
        students = db.query(UserModel.student_id).filter(
            UserModel.role == "student",
            UserModel.class_id == r.class_id,
        ).all()
        student_ids = [s[0] for s in students]

        avg_score = 0.0
        if student_ids:
            score_row = db.query(func.avg(QuizResultModel.score)).filter(
                QuizResultModel.student_id.in_(student_ids)
            ).first()
            avg_score = round(float(score_row[0] or 0), 1)

        points_row = db.query(func.avg(PointsModel.total_points)).filter(
            PointsModel.student_id.in_(student_ids)
        ).first()
        avg_points = round(float(points_row[0] or 0), 1)

        hours_row = db.query(func.sum(LearningRecordModel.duration)).filter(
            LearningRecordModel.student_id.in_(student_ids)
        ).first()
        total_hours = round(float(hours_row[0] or 0) / 3600, 1)

        classes.append({
            "class_id": r.class_id,
            "student_count": r.student_count,
            "avg_score": avg_score,
            "avg_points": avg_points,
            "total_hours": total_hours,
        })
    return {"status": "success", "classes": classes, "total": len(classes)}


@router.get("/class-comparison")
async def get_class_comparison(
    days: int = Query(30, ge=1, le=90),
    db: Session = Depends(get_db),
    _current: str = Depends(require_teacher),
):
    """班级间对比（试点"实验组 vs 对照组"数据源）"""
    from ..models.knowledge import LearningRecordModel, QuizResultModel

    since = datetime.now(timezone.utc) - timedelta(days=days)
    rows = db.query(
        UserModel.class_id,
        func.count(func.distinct(UserModel.student_id)).label("student_count"),
    ).filter(
        UserModel.role == "student",
        UserModel.class_id.isnot(None),
    ).group_by(UserModel.class_id).all()

    result = []
    for r in rows:
        students = db.query(UserModel.student_id).filter(
            UserModel.role == "student",
            UserModel.class_id == r.class_id,
        ).all()
        student_ids = [s[0] for s in students]

        # 平均分
        score_row = db.query(func.avg(QuizResultModel.score)).filter(
            QuizResultModel.student_id.in_(student_ids),
            QuizResultModel.created_at >= since,
        ).first()
        # 总时长
        hours_row = db.query(func.sum(LearningRecordModel.duration)).filter(
            LearningRecordModel.student_id.in_(student_ids),
            LearningRecordModel.created_at >= since,
        ).first()
        # 人均记录
        rec_row = db.query(
            func.count(LearningRecordModel.record_id),
            func.count(func.distinct(LearningRecordModel.student_id)),
        ).filter(
            LearningRecordModel.student_id.in_(student_ids),
            LearningRecordModel.created_at >= since,
        ).first()
        # 完成知识点数
        done_row = db.query(func.count(func.distinct(LearningRecordModel.kp_id))).filter(
            LearningRecordModel.student_id.in_(student_ids),
            LearningRecordModel.created_at >= since,
            LearningRecordModel.progress >= 0.8,
        ).first()

        result.append({
            "class_id": r.class_id,
            "student_count": r.student_count,
            "avg_score": round(float(score_row[0] or 0), 1),
            "total_hours": round(float(hours_row[0] or 0) / 3600, 1),
            "avg_records_per_student": round(float(rec_row[0] or 0) / max(int(rec_row[1] or 1), 1), 1),
            "completed_kps": done_row[0] or 0,
        })

    result.sort(key=lambda c: -c["student_count"])
    return {"status": "success", "period_days": days, "classes": result}


@router.get("/overview")
async def get_overview(
    db: Session = Depends(get_db),
    _current: str = Depends(require_teacher)
):
    """全班概览统计"""
    total_students = db.query(UserModel).filter(UserModel.role == "student").count()

    # 活跃学生（最近7天有学习记录）
    from datetime import datetime, timedelta
    week_ago = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
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
    limit: int = Query(50, ge=1, le=200),
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
    limit: int = Query(30, ge=1, le=200),
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
    days: int = Query(30, ge=1, le=90),
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
    limit: int = Query(20, ge=1, le=100),
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
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _current: str = Depends(require_teacher)
):
    """学生排行榜"""
    students = db.query(UserModel).filter(UserModel.role == "student").all()
    student_ids = [s.student_id for s in students]
    points_by_student = dict(
        db.query(PointsModel.student_id, func.max(PointsModel.total_points))
        .filter(PointsModel.student_id.in_(student_ids))
        .group_by(PointsModel.student_id).all()
    ) if student_ids else {}
    duration_by_student = dict(
        db.query(LearningRecordModel.student_id, func.sum(LearningRecordModel.duration))
        .filter(LearningRecordModel.student_id.in_(student_ids))
        .group_by(LearningRecordModel.student_id).all()
    ) if student_ids else {}
    score_by_student = dict(
        db.query(QuizResultModel.student_id, func.avg(QuizResultModel.score))
        .filter(QuizResultModel.student_id.in_(student_ids))
        .group_by(QuizResultModel.student_id).all()
    ) if student_ids else {}
    ranking = []

    for s in students:
        total_duration = duration_by_student.get(s.student_id, 0) or 0
        avg_score = score_by_student.get(s.student_id)

        ranking.append({
            "student_id": s.student_id,
            "username": s.username,
            "total_points": points_by_student.get(s.student_id, 0),
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


# ---------- 导出 ----------
class ExportRequest(BaseModel):
    report_type: str = Field(..., pattern="^(scores|progress|ranking|all)$")
    format: str = Field("csv", pattern="^csv$")
    student_ids: Optional[List[str]] = Field(None, max_length=500)


@router.get("/exports")
async def get_export_records(
    db: Session = Depends(get_db),
    _current: str = Depends(require_teacher)
):
    """获取导出记录列表"""
    return {
        "status": "success",
        "exports": [],
        "total": 0,
    }


@router.post("/export")
async def export_report(
    request: ExportRequest,
    db: Session = Depends(get_db),
    _current: str = Depends(require_teacher),
):
    """导出学生成绩/进度报表，返回 CSV 文件"""
    import csv
    import io
    from datetime import datetime, timezone

    if request.report_type not in {"scores", "progress", "ranking", "all"}:
        raise HTTPException(status_code=422, detail="report_type 必须是 scores、progress、ranking 或 all")
    if request.format != "csv":
        raise HTTPException(status_code=422, detail="当前仅支持 csv 格式")

    # 查询学生
    query = db.query(UserModel).filter(UserModel.role == "student")
    if request.student_ids:
        query = query.filter(UserModel.student_id.in_(request.student_ids))
    students = query.all()
    student_ids = [s.student_id for s in students]
    if not students:
        rows, fieldnames, title = [], [], ""
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        output.seek(0)
        return StreamingResponse(iter([output.getvalue().encode("utf-8-sig")]), media_type="text/csv")
    points_by_student = dict(
        db.query(PointsModel.student_id, func.max(PointsModel.total_points))
        .filter(PointsModel.student_id.in_(student_ids))
        .group_by(PointsModel.student_id).all()
    )
    records_by_student = defaultdict(list)
    for record in db.query(LearningRecordModel).filter(LearningRecordModel.student_id.in_(student_ids)).all():
        records_by_student[record.student_id].append(record)
    quizzes_by_student = defaultdict(list)
    for quiz in db.query(QuizResultModel).filter(QuizResultModel.student_id.in_(student_ids)).all():
        quizzes_by_student[quiz.student_id].append(quiz)
    latest_trend_date = db.query(
        TrendDataModel.student_id, func.max(TrendDataModel.date).label("latest_date")
    ).filter(TrendDataModel.student_id.in_(student_ids)).group_by(TrendDataModel.student_id).subquery()
    trends_by_student = {
        row.student_id: row for row in db.query(TrendDataModel).join(
            latest_trend_date,
            (TrendDataModel.student_id == latest_trend_date.c.student_id)
            & (TrendDataModel.date == latest_trend_date.c.latest_date),
        ).all()
    }

    if request.report_type == "scores":
        rows = []
        for s in students:
            quizzes = quizzes_by_student.get(s.student_id, [])
            if quizzes:
                avg = round(sum(q.score for q in quizzes) / len(quizzes), 1)
                rows.append({
                    "student_id": s.student_id,
                    "username": s.username,
                    "quiz_count": len(quizzes),
                    "avg_score": avg,
                    "max_score": max(q.score for q in quizzes),
                    "min_score": min(q.score for q in quizzes),
                })
            else:
                rows.append({
                    "student_id": s.student_id,
                    "username": s.username,
                    "quiz_count": 0,
                    "avg_score": 0,
                    "max_score": 0,
                    "min_score": 0,
                })
        fieldnames = ["student_id", "username", "quiz_count", "avg_score", "max_score", "min_score"]
        title = "成绩报表"

    elif request.report_type == "progress":
        rows = []
        for s in students:
            records = records_by_student.get(s.student_id, [])
            total_duration = sum(r.duration or 0 for r in records)
            completed = sum(1 for r in records if r.action == "complete")
            rows.append({
                "student_id": s.student_id,
                "username": s.username,
                "total_records": len(records),
                "total_hours": round(total_duration / 3600, 1),
                "completed_kps": completed,
            })
        fieldnames = ["student_id", "username", "total_records", "total_hours", "completed_kps"]
        title = "学习进度报表"

    elif request.report_type == "ranking":
        rows = []
        for s in students:
            points = points_by_student.get(s.student_id, 0)
            records = records_by_student.get(s.student_id, [])
            total_duration = sum(r.duration or 0 for r in records)
            quizzes = quizzes_by_student.get(s.student_id, [])
            avg_score_q = (sum(q.score or 0 for q in quizzes) / len(quizzes)) if quizzes else 0
            trend = trends_by_student.get(s.student_id)
            rows.append({
                "student_id": s.student_id,
                "username": s.username,
                "total_points": points_by_student.get(s.student_id, 0),
                "total_hours": round(total_duration / 3600, 1),
                "avg_score": round(avg_score_q, 1) if avg_score_q else 0,
                "trend_state": trend.trend_state if trend else "unknown",
            })
        rows.sort(key=lambda x: x["total_points"], reverse=True)
        for i, r in enumerate(rows):
            r["rank"] = i + 1
        fieldnames = ["rank", "student_id", "username", "total_points", "total_hours", "avg_score", "trend_state"]
        title = "学生排行榜"

    else:  # all
        rows = []
        for s in students:
            points = points_by_student.get(s.student_id, 0)
            records = records_by_student.get(s.student_id, [])
            total_duration = sum(r.duration or 0 for r in records)
            completed = sum(1 for r in records if r.action == "complete")
            quizzes = quizzes_by_student.get(s.student_id, [])
            avg_score_q = (sum(q.score or 0 for q in quizzes) / len(quizzes)) if quizzes else 0
            trend = trends_by_student.get(s.student_id)
            rows.append({
                "student_id": s.student_id,
                "username": s.username,
                "total_points": points_by_student.get(s.student_id, 0),
                "total_hours": round(total_duration / 3600, 1),
                "completed_kps": completed,
                "quiz_count": len(quizzes),
                "avg_score": round(avg_score_q, 1) if avg_score_q else 0,
                "trend_state": trend.trend_state if trend else "unknown",
            })
        fieldnames = ["student_id", "username", "total_points", "total_hours", "completed_kps", "quiz_count", "avg_score", "trend_state"]
        title = "综合报表"

    # 生成 CSV
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

    from fastapi.responses import StreamingResponse
    output.seek(0)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"{title}_{timestamp}.csv"

    # UTF-8 BOM for Excel compatibility with Chinese characters
    bom_output = "﻿" + output.getvalue()

    from urllib.parse import quote
    encoded_filename = quote(filename, safe="")

    return StreamingResponse(
        iter([bom_output.encode("utf-8")]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"},
    )


# ---------- 教学资源 ----------
@router.get("/resources")
async def get_teaching_resources(
    db: Session = Depends(get_db),
    _current: str = Depends(require_teacher)
):
    """获取教学资源列表"""
    # 从PPT任务中获取已生成的资源
    from .ppt import _ppt_tasks
    resources = []
    for task_id, task in _ppt_tasks.items():
        if task.get("status") == "completed":
            resources.append({
                "resource_id": task_id,
                "name": task.get("filename", f"PPT_{task_id}.pptx"),
                "type": "PPT",
                "created_at": task.get("created_at", ""),
                "status": "completed",
                "download_url": f"/api/v1/ppt/{task_id}/download",
            })
    return {
        "status": "success",
        "resources": resources,
        "total": len(resources),
    }


# ---------- 系统信息 ----------
@router.get("/system-info")
async def get_system_info(
    _current: str = Depends(require_teacher)
):
    """获取系统信息"""
    from datetime import datetime, timezone

    return {
        "status": "success",
        "system_info": {
            "version": "1.0.0",
            "ai_model": "MiMo v2.5 Pro",
            "database_status": "normal",
            "last_updated": datetime.now(timezone.utc).isoformat(),
        },
    }


# ---------- 学习预警 ----------
@router.get("/alerts")
async def get_learning_alerts(
    db: Session = Depends(get_db),
    _current: str = Depends(require_teacher)
):
    """获取学习预警列表 —— 多维度风险检测"""
    from datetime import datetime, timedelta

    alerts = []
    students = db.query(UserModel).filter(UserModel.role == "student").all()
    now = datetime.utcnow()
    # Use strftime to match SQLite's datetime format (no 'T', no timezone suffix)
    week_ago = (now - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
    two_weeks_ago = (now - timedelta(days=14)).strftime("%Y-%m-%d %H:%M:%S")

    for s in students:
        sid = s.student_id
        reasons = []

        # 1. 近7天无学习记录
        recent_records = db.query(LearningRecordModel).filter(
            LearningRecordModel.student_id == sid,
            LearningRecordModel.created_at >= week_ago,
        ).count()
        if recent_records == 0:
            reasons.append({"text": "近7天无学习记录", "suggestion": "建议安排一对一沟通了解学习状态"})

        # 2. 测验平均分低于60
        avg_score = db.query(func.avg(QuizResultModel.score)).filter(
            QuizResultModel.student_id == sid
        ).scalar()
        if avg_score is not None and avg_score < 60:
            reasons.append({"text": f"测验平均分偏低 ({round(avg_score, 1)}分)", "suggestion": "建议安排知识点补习和针对性练习"})

        # 3. 趋势下滑
        trend = db.query(TrendDataModel).filter(
            TrendDataModel.student_id == sid
        ).order_by(TrendDataModel.date.desc()).first()
        if trend and trend.trend_state in ("decline", "warning"):
            state_text = "下滑" if trend.trend_state == "decline" else "预警"
            reasons.append({"text": f"学习趋势{state_text}", "suggestion": "建议分析近期学习内容难度，适当降低或调整学习路径"})

        # 4. 薄弱知识点过多
        profile = db.query(StudentProfileModel).filter(
            StudentProfileModel.student_id == sid
        ).first()
        if profile and profile.weak_areas and len(profile.weak_areas) >= 5:
            reasons.append({"text": f"薄弱知识点过多 ({len(profile.weak_areas)}个)", "suggestion": "建议制定专项突破计划，重点攻克核心知识点"})

        # 5. 测验趋势下降（近7天正确率 vs 前7天）
        recent_stats = db.query(
            func.sum(QuizResultModel.correct_count),
            func.sum(QuizResultModel.total_questions),
        ).filter(
            QuizResultModel.student_id == sid,
            QuizResultModel.created_at >= week_ago,
        ).first()
        recent_correct = recent_stats[0] or 0
        recent_total = recent_stats[1] or 0

        prev_stats = db.query(
            func.sum(QuizResultModel.correct_count),
            func.sum(QuizResultModel.total_questions),
        ).filter(
            QuizResultModel.student_id == sid,
            QuizResultModel.created_at >= two_weeks_ago,
            QuizResultModel.created_at < week_ago,
        ).first()
        prev_correct = prev_stats[0] or 0
        prev_total = prev_stats[1] or 0

        if recent_total >= 3 and prev_total >= 3:
            recent_acc = recent_correct / recent_total
            prev_acc = prev_correct / prev_total
            if prev_acc - recent_acc > 0.2:
                reasons.append({"text": f"测验正确率下降{round((prev_acc - recent_acc) * 100)}% (前{round(prev_acc*100)}%→近{round(recent_acc*100)}%)", "suggestion": "建议关注学习状态变化，排查是否有知识断层"})
            elif recent_acc < 0.3:
                reasons.append({"text": f"近期测验正确率过低 ({round(recent_acc*100)}%)", "suggestion": "建议降低题目难度，加强基础巩固"})

        # 6. 错题积压（total_questions - correct_count）
        wrong_stats = db.query(
            func.sum(QuizResultModel.total_questions - QuizResultModel.correct_count),
        ).filter(
            QuizResultModel.student_id == sid,
        ).scalar() or 0
        if wrong_stats >= 10:
            reasons.append({"text": f"未纠正错题过多 ({wrong_stats}题)", "suggestion": "建议安排错题复习，逐一攻克易错知识点"})
        elif wrong_stats >= 5:
            reasons.append({"text": f"错题积压 ({wrong_stats}题)", "suggestion": "建议定期回顾错题，防止同类错误反复"})

        if reasons:
            level = "high" if len(reasons) >= 3 else ("medium" if len(reasons) >= 2 else "low")
            alerts.append({
                "student_id": sid,
                "username": s.username,
                "reasons": reasons,
                "level": level,
                "avg_score": round(avg_score, 1) if avg_score else None,
                "recent_records": recent_records,
            })

    alerts.sort(key=lambda x: (0 if x["level"] == "high" else 1 if x["level"] == "medium" else 2, -len(x["reasons"])))

    return {
        "status": "success",
        "alerts": alerts,
        "total": len(alerts),
        "high_risk": sum(1 for a in alerts if a["level"] == "high"),
        "medium_risk": sum(1 for a in alerts if a["level"] == "medium"),
    }


# ---------- 试点数据分析报告（AIC 应用效果验证） ----------

@router.get("/pilot-report")
async def get_pilot_report(
    days: int = Query(30, ge=1, le=90),
    student_id: Optional[str] = Query(None, description="不传=全班汇总"),
    class_id: Optional[str] = Query(None, description="按班级过滤（试点实验组/对照组）"),
    format: str = Query("json", description="json 或 markdown（导出参赛文档素材）"),
    db: Session = Depends(get_db),
    _teacher: str = Depends(require_teacher),
):
    """试点数据分析报告（AIC"应用效果"评分项的验证数据源）

    聚合五个维度：学习行为 / 测验成绩 / 掌握度趋势 / 实验参与 / 功能使用
    支持按班级过滤（class_id），输出可直接用于参赛文档的效果验证章节。
    """
    from datetime import timedelta, timezone
    from ..models.experiment import ExperimentLogModel

    # 班级过滤：取该班学生 id 列表
    class_student_ids: Optional[List[str]] = None
    if class_id:
        class_student_ids = [
            u.student_id
            for u in db.query(UserModel).filter(
                UserModel.role == "student",
                UserModel.class_id == class_id,
            ).all()
        ]
        if not class_student_ids:
            return {"status": "success", "period_days": days, "scope": f"class:{class_id}",
                    "summary": {"active_students": 0}, "students": []}
    from ..models.monitor import ApiMonitorModel

    since = datetime.now(timezone.utc) - timedelta(days=days)

    def _scope_filter(model):
        """班级/学生作用域过滤条件"""
        if student_id:
            return model.student_id == student_id
        if class_student_ids:
            return model.student_id.in_(class_student_ids)
        return None

    # ---------- 1. 学习行为（learning_records） ----------
    lq = db.query(
        LearningRecordModel.student_id,
        func.count().label("record_count"),
        func.coalesce(func.sum(LearningRecordModel.duration), 0).label("total_duration"),
    ).filter(LearningRecordModel.created_at >= since)
    _sf = _scope_filter(LearningRecordModel)
    if _sf is not None:
        lq = lq.filter(_sf)
    lq = lq.group_by(LearningRecordModel.student_id)
    learn_rows = lq.all()

    # 知识点完成度
    cq = db.query(
        LearningRecordModel.student_id,
        func.count(func.distinct(LearningRecordModel.kp_id)).label("kp_count"),
    ).filter(
        LearningRecordModel.created_at >= since,
        LearningRecordModel.progress >= 0.8,
    )
    _sf = _scope_filter(LearningRecordModel)
    if _sf is not None:
        cq = cq.filter(_sf)
    cq = cq.group_by(LearningRecordModel.student_id)
    complete_map = {r.student_id: r.kp_count for r in cq.all()}

    # ---------- 2. 测验成绩（quiz_results） ----------
    zq = db.query(
        QuizResultModel.student_id,
        func.count().label("quiz_count"),
        func.avg(QuizResultModel.score).label("avg_score"),
        func.max(QuizResultModel.score).label("max_score"),
        func.min(QuizResultModel.score).label("min_score"),
    ).filter(QuizResultModel.created_at >= since)
    _sf = _scope_filter(QuizResultModel)
    if _sf is not None:
        zq = zq.filter(_sf)
    zq = zq.group_by(QuizResultModel.student_id)
    quiz_map = {r.student_id: r for r in zq.all()}

    # 前后测对比（全班/班级）：前1/3 vs 后1/3 平均分
    pre_post = None
    if not student_id:
        pq = db.query(QuizResultModel.score).filter(QuizResultModel.created_at >= since)
        _sf = _scope_filter(QuizResultModel)
        if _sf is not None:
            pq = pq.filter(_sf)
        all_scores = pq.order_by(QuizResultModel.created_at.asc()).all()
        n = len(all_scores)
        if n >= 6:
            third = n // 3
            pre = sum(s[0] for s in all_scores[:third]) / third
            post = sum(s[0] for s in all_scores[-third:]) / third
            pre_post = {"pre_avg": round(pre, 1), "post_avg": round(post, 1),
                        "improvement": round(post - pre, 1), "sample_size": n}

    # ---------- 3. 掌握度趋势（student_trends） ----------
    tq = db.query(
        TrendDataModel.student_id,
        TrendDataModel.trend_state,
        func.count().label("count"),
    ).filter(TrendDataModel.created_at >= since)
    _sf = _scope_filter(TrendDataModel)
    if _sf is not None:
        tq = tq.filter(_sf)
    tq = tq.group_by(TrendDataModel.student_id, TrendDataModel.trend_state)
    trend_map: Dict[str, int] = {}
    for r in tq.all():
        trend_map[r.trend_state] = trend_map.get(r.trend_state, 0) + r.count

    # ---------- 4. 实验参与（experiment_logs） ----------
    eq = db.query(
        ExperimentLogModel.experiment_type,
        func.count().label("count"),
    ).filter(ExperimentLogModel.created_at >= since)
    _sf = _scope_filter(ExperimentLogModel)
    if _sf is not None:
        eq = eq.filter(_sf)
    eq = eq.group_by(ExperimentLogModel.experiment_type)
    experiment_map = {r.experiment_type: r.count for r in eq.all()}

    # ---------- 5. 功能使用（api_monitor，仅登录用户行为） ----------
    from .monitoring import _map_feature
    fq = db.query(
        ApiMonitorModel.endpoint,
        func.count().label("count"),
    ).filter(
        ApiMonitorModel.created_at >= since,
        ApiMonitorModel.student_id.isnot(None),
    )
    _sf = _scope_filter(ApiMonitorModel)
    if _sf is not None:
        fq = fq.filter(_sf)
    fq = fq.group_by(ApiMonitorModel.endpoint).all()
    feature_map: Dict[str, int] = {}
    for r in fq:
        fname = _map_feature(r.endpoint)
        feature_map[fname] = feature_map.get(fname, 0) + r.count
    top_features = sorted(feature_map.items(), key=lambda x: -x[1])[:10]

    # ---------- 汇总 ----------
    students = []
    for r in learn_rows:
        q = quiz_map.get(r.student_id)
        students.append({
            "student_id": r.student_id,
            "record_count": r.record_count,
            "total_duration_sec": r.total_duration,
            "total_duration_hours": round(r.total_duration / 3600, 1),
            "completed_kps": complete_map.get(r.student_id, 0),
            "quiz_count": q.quiz_count if q else 0,
            "avg_score": round(q.avg_score, 1) if q and q.avg_score else 0,
            "max_score": q.max_score if q else 0,
        })
    students.sort(key=lambda s: -s["total_duration_sec"])

    total_duration = sum(s["total_duration_sec"] for s in students)
    total_quiz = sum(s["quiz_count"] for s in students)
    report = {
        "status": "success",
        "period_days": days,
        "scope": class_id or ("student" if student_id else "class"),
        "summary": {
            "active_students": len(students),
            "total_duration_hours": round(total_duration / 3600, 1),
            "avg_daily_hours": round(total_duration / 3600 / max(days, 1), 2),
            "total_records": sum(s["record_count"] for s in students),
            "total_quizzes": total_quiz,
            "avg_score": round(sum(s["avg_score"] for s in students) / max(len(students), 1), 1),
            "total_experiments": sum(experiment_map.values()),
            "completed_kps_total": sum(s["completed_kps"] for s in students),
        },
        "quiz_pre_post": pre_post,
        "trend_distribution": trend_map,
        "experiments": experiment_map,
        "top_features": [{"feature": k, "count": v} for k, v in top_features],
        "students": students,
    }

    # ---------- Markdown 导出（参赛文档素材） ----------
    if format == "markdown":
        s = report["summary"]
        lines = [
            "# LearnLab 试点数据分析报告",
            "",
            f"- 统计周期：近 {days} 天",
            f"- 统计范围：{report['scope']}",
            f"- 生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}",
            "",
            "## 一、总体概览",
            "",
            "| 指标 | 数值 |",
            "|---|---|",
            f"| 活跃学生数 | {s['active_students']} |",
            f"| 总学习时长 | {s['total_duration_hours']} 小时 |",
            f"| 日均学习时长 | {s['avg_daily_hours']} 小时 |",
            f"| 学习记录总数 | {s['total_records']} |",
            f"| 测验总次数 | {s['total_quizzes']} |",
            f"| 平均测验分 | {s['avg_score']} |",
            f"| 实验参与次数 | {s['total_experiments']} |",
            f"| 掌握知识点总数 | {s['completed_kps_total']} |",
            "",
        ]
        if pre_post:
            lines += [
                "## 二、前后测成绩对比",
                "",
                f"- 前测平均分：{pre_post['pre_avg']}",
                f"- 后测平均分：{pre_post['post_avg']}",
                f"- 提升幅度：**+{pre_post['improvement']} 分**（样本 {pre_post['sample_size']} 次测验）",
                "",
            ]
        if experiment_map:
            lines += [
                "## 三、实验参与分布",
                "",
                "| 实验类型 | 次数 |",
                "|---|---|",
            ]
            labels = {"circuit_simulate": "模拟电路仿真", "circuit_fault": "故障诊断实验",
                      "stm32_simulate": "STM32仿真", "stm32_experiment": "STM32实验实训"}
            for k, v in experiment_map.items():
                lines.append(f"| {labels.get(k, k)} | {v} |")
            lines.append("")
        if top_features:
            lines += ["## 四、功能使用 Top", ""]
            for f_name, f_count in top_features[:5]:
                lines.append(f"- {f_name}：{f_count} 次")
            lines.append("")
        if trend_map:
            labels_t = {"growth": "成长", "stable": "稳定", "decline": "下滑", "warning": "预警"}
            lines += ["## 五、学习趋势分布", ""]
            for k, v in trend_map.items():
                lines.append(f"- {labels_t.get(k, k)}：{v}")
            lines.append("")
        if students:
            lines += ["## 六、学生明细", "", "| 学生 | 记录数 | 时长(h) | 掌握知识点 | 测验 | 平均分 |", "|---|---|---|---|---|---|"]
            for st in students:
                lines.append(f"| {st['student_id']} | {st['record_count']} | {st['total_duration_hours']} | {st['completed_kps']} | {st['quiz_count']} | {st['avg_score']} |")
            lines.append("")
        report["markdown"] = "\n".join(lines)
    return report
