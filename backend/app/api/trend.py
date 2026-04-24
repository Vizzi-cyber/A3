"""
学习趋势与评估API
- 预测、报告、预警
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from ..models.database import get_db
from ..models.knowledge import QuizResultModel, LearningRecordModel
from ..models.student import StudentProfileModel
from ..models.trend import TrendDataModel
from ..algorithms import MultiFactorTrendAnalyzer, LearningEffectEvaluator

router = APIRouter()


class TrendAnalyzeRequest(BaseModel):
    student_id: str


@router.post("/analyze")
async def analyze_trend(request: TrendAnalyzeRequest, db: Session = Depends(get_db)):
    """多因素趋势分析"""
    student_id = request.student_id

    # 查询数据（限制最近 90 天，避免全表扫描）
    since = datetime.now() - timedelta(days=90)
    quizzes = db.query(QuizResultModel).filter(QuizResultModel.student_id == student_id, QuizResultModel.created_at >= since).order_by(QuizResultModel.created_at).all()
    records = db.query(LearningRecordModel).filter(LearningRecordModel.student_id == student_id, LearningRecordModel.created_at >= since).order_by(LearningRecordModel.created_at).all()
    profile = db.query(StudentProfileModel).filter(StudentProfileModel.student_id == student_id).first()

    quiz_history = [
        {
            "score": q.score,
            "correct_count": q.correct_count,
            "total_questions": q.total_questions,
            "weak_tags": q.weak_tags or [],
            "created_at": q.created_at.isoformat() if q.created_at else None,
        }
        for q in quizzes
    ]
    learning_history = [
        {
            "duration": r.duration,
            "progress": r.progress,
            "action": r.action,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in records
    ]
    weak_areas = profile.weak_areas or [] if profile else []

    analyzer = MultiFactorTrendAnalyzer()
    result = analyzer.analyze(
        student_id=student_id,
        quiz_history=quiz_history,
        learning_records=learning_history,
        weak_areas=weak_areas,
        profile={"learning_tempo": profile.learning_tempo or {}} if profile else {},
    )

    # 持久化趋势数据
    today = datetime.now().strftime("%Y-%m-%d")
    existing = db.query(TrendDataModel).filter(
        TrendDataModel.student_id == student_id,
        TrendDataModel.date == today,
    ).first()
    if existing:
        existing.trend_factor = result["trend_factor"]
        existing.trend_state = result["trend_state"]
        existing.mastery_trend = result["dimensions"]["mastery_trend"]
        existing.speed_ratio = result["dimensions"]["speed_ratio"]
        existing.time_efficiency = result["dimensions"]["time_efficiency"]
        existing.weakness_priority = result["dimensions"]["weakness_priority"]
        existing.stability = result["dimensions"]["stability"]
        existing.predicted_mastery_3d = result["predicted_mastery_3d"]
        existing.intervention = result["intervention"]
    else:
        trend = TrendDataModel(
            student_id=student_id,
            date=today,
            trend_factor=result["trend_factor"],
            trend_state=result["trend_state"],
            mastery_trend=result["dimensions"]["mastery_trend"],
            speed_ratio=result["dimensions"]["speed_ratio"],
            time_efficiency=result["dimensions"]["time_efficiency"],
            weakness_priority=result["dimensions"]["weakness_priority"],
            stability=result["dimensions"]["stability"],
            predicted_mastery_3d=result["predicted_mastery_3d"],
            intervention=result["intervention"],
        )
        db.add(trend)
    db.commit()

    return {"status": "success", "data": result}


@router.get("/{student_id}/report")
async def get_eval_report(student_id: str, db: Session = Depends(get_db)):
    """学习效果评估报告"""
    since = datetime.now() - timedelta(days=90)
    quizzes = db.query(QuizResultModel).filter(QuizResultModel.student_id == student_id, QuizResultModel.created_at >= since).order_by(QuizResultModel.created_at).all()
    records = db.query(LearningRecordModel).filter(LearningRecordModel.student_id == student_id, LearningRecordModel.created_at >= since).order_by(LearningRecordModel.created_at).all()
    profile = db.query(StudentProfileModel).filter(StudentProfileModel.student_id == student_id).first()
    weak_areas = profile.weak_areas or [] if profile else []

    quiz_history = [
        {
            "score": q.score,
            "correct_count": q.correct_count,
            "total_questions": q.total_questions,
            "weak_tags": q.weak_tags or [],
        }
        for q in quizzes
    ]
    learning_history = [
        {
            "duration": r.duration,
            "progress": r.progress,
        }
        for r in records
    ]

    evaluator = LearningEffectEvaluator()
    report = evaluator.evaluate(
        student_id=student_id,
        quiz_history=quiz_history,
        learning_records=learning_history,
        weak_areas=weak_areas,
    )
    return {"status": "success", "data": report}


@router.get("/{student_id}/history")
async def get_trend_history(student_id: str, days: int = 30, db: Session = Depends(get_db)):
    """获取历史趋势数据"""
    trends = (
        db.query(TrendDataModel)
        .filter(TrendDataModel.student_id == student_id)
        .order_by(TrendDataModel.date.desc())
        .limit(days)
        .all()
    )
    return {
        "status": "success",
        "student_id": student_id,
        "data": [
            {
                "date": t.date,
                "trend_factor": t.trend_factor,
                "trend_state": t.trend_state,
                "dimensions": {
                    "mastery_trend": t.mastery_trend,
                    "speed_ratio": t.speed_ratio,
                    "time_efficiency": t.time_efficiency,
                    "weakness_priority": t.weakness_priority,
                    "stability": t.stability,
                },
                "predicted_mastery_3d": t.predicted_mastery_3d,
                "intervention": t.intervention,
            }
            for t in trends
        ],
    }
