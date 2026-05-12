"""
学习挑战 & 增强排行榜 API
从现有数据计算，不新增数据库表
"""
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func as sa_func

from ..models.database import get_db
from ..models.knowledge import LearningRecordModel, QuizResultModel, KnowledgePointModel
from ..models.gamification import PointsModel, AchievementModel, TaskModel
from ..models.student import StudentProfileModel

router = APIRouter()


def _safe_float(v, default=0.0):
    try:
        return float(v) if v is not None else default
    except (ValueError, TypeError):
        return default


# ---------- 学习挑战 ----------

# 挑战定义（硬编码，不依赖数据库）
CHALLENGE_DEFS = [
    {
        "id": "daily_learner",
        "name": "每日学习者",
        "description": "今天完成3个知识点的学习",
        "type": "daily",
        "target": 3,
        "reward": 50,
        "icon": "book",
        "difficulty": 1,
    },
    {
        "id": "quiz_master",
        "name": "测验达人",
        "description": "完成2次测验且均分≥80",
        "type": "daily",
        "target": 2,
        "reward": 80,
        "icon": "trophy",
        "difficulty": 2,
    },
    {
        "id": "streak_warrior",
        "name": "连续学习战士",
        "description": "保持连续学习3天以上",
        "type": "weekly",
        "target": 3,
        "reward": 100,
        "icon": "fire",
        "difficulty": 2,
    },
    {
        "id": "knowledge_explorer",
        "name": "知识探索者",
        "description": "学习5个不同的知识点",
        "type": "weekly",
        "target": 5,
        "reward": 120,
        "icon": "compass",
        "difficulty": 3,
    },
    {
        "id": "perfect_score",
        "name": "满分王者",
        "description": "任意一次测验获得100分",
        "type": "challenge",
        "target": 1,
        "reward": 200,
        "icon": "crown",
        "difficulty": 4,
    },
    {
        "id": "marathon_learner",
        "name": "马拉松学习者",
        "description": "单日学习时长超过2小时",
        "type": "challenge",
        "target": 120,
        "reward": 150,
        "icon": "clock",
        "difficulty": 3,
    },
    {
        "id": "weakness_breaker",
        "name": "弱点突破者",
        "description": "在薄弱知识点上测验得分≥70",
        "type": "challenge",
        "target": 1,
        "reward": 180,
        "icon": "thunder",
        "difficulty": 3,
    },
    {
        "id": "five_star_student",
        "name": "五星学员",
        "description": "累计获得5个成就徽章",
        "type": "milestone",
        "target": 5,
        "reward": 300,
        "icon": "star",
        "difficulty": 5,
    },
]


@router.get("/{student_id}/challenges")
def get_challenges(student_id: str, db: Session = Depends(get_db)):
    """获取挑战列表及进度"""

    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=today_start.weekday())

    # 查询今日学习记录
    today_records = db.query(LearningRecordModel).filter(
        LearningRecordModel.student_id == student_id,
        LearningRecordModel.created_at >= today_start,
    ).all()

    today_kps = set(r.kp_id for r in today_records)

    # 查询今日测验
    today_quizzes = db.query(QuizResultModel).filter(
        QuizResultModel.student_id == student_id,
        QuizResultModel.created_at >= today_start,
    ).all()

    # 查询本周记录
    week_records = db.query(LearningRecordModel).filter(
        LearningRecordModel.student_id == student_id,
        LearningRecordModel.created_at >= week_start,
    ).all()

    week_kps = set(r.kp_id for r in week_records)

    # 连续学习天数
    all_records = db.query(LearningRecordModel).filter(
        LearningRecordModel.student_id == student_id,
    ).all()

    dates = set()
    for r in all_records:
        if r.created_at:
            dates.add(r.created_at.strftime("%Y-%m-%d"))
    sorted_dates = sorted(dates, reverse=True)
    streak = 0
    for i, d in enumerate(sorted_dates):
        expected = (now.date() - timedelta(days=i)).isoformat()
        if d == expected:
            streak += 1
        else:
            break

    # 成就数
    achievement_count = db.query(AchievementModel).filter(
        AchievementModel.student_id == student_id,
    ).count()

    # 全部测验
    all_quizzes = db.query(QuizResultModel).filter(
        QuizResultModel.student_id == student_id,
    ).all()

    # 今日学习时长（分钟）
    today_duration = sum(r.duration or 0 for r in today_records) / 60.0

    # 计算每个挑战的进度
    challenges = []
    for ch in CHALLENGE_DEFS:
        progress = 0
        completed = False

        if ch["id"] == "daily_learner":
            progress = len(today_kps)
        elif ch["id"] == "quiz_master":
            good_quizzes = [q for q in today_quizzes if q.score and q.score >= 80]
            progress = len(good_quizzes)
        elif ch["id"] == "streak_warrior":
            progress = streak
        elif ch["id"] == "knowledge_explorer":
            progress = len(week_kps)
        elif ch["id"] == "perfect_score":
            perfect = [q for q in all_quizzes if q.score == 100]
            progress = 1 if perfect else 0
        elif ch["id"] == "marathon_learner":
            progress = int(today_duration)
        elif ch["id"] == "weakness_breaker":
            # 简化：今日测验≥70即算
            weak_pass = [q for q in today_quizzes if q.score and q.score >= 70]
            progress = 1 if weak_pass else 0
        elif ch["id"] == "five_star_student":
            progress = achievement_count

        completed = progress >= ch["target"]
        challenges.append({
            **ch,
            "progress": min(progress, ch["target"]),
            "completed": completed,
            "progress_pct": min(100, round(progress / ch["target"] * 100)),
        })

    # 挑战地图节点（按难度排序，形成路径）
    map_nodes = []
    for i, ch in enumerate(sorted(challenges, key=lambda x: x["difficulty"])):
        map_nodes.append({
            "node_id": i + 1,
            "challenge_id": ch["id"],
            "name": ch["name"],
            "difficulty": ch["difficulty"],
            "completed": ch["completed"],
            "x": 50 + (i % 4) * 200,
            "y": 100 + (i // 4) * 180,
        })

    return {
        "status": "success",
        "data": {
            "challenges": challenges,
            "map_nodes": map_nodes,
            "summary": {
                "total": len(challenges),
                "completed": sum(1 for c in challenges if c["completed"]),
                "total_reward": sum(c["reward"] for c in challenges if c["completed"]),
                "streak_days": streak,
            },
        },
    }


# ---------- 增强排行榜 ----------

@router.get("/leaderboard/{dimension}")
def get_leaderboard(
    dimension: str,
    period: str = Query("weekly", regex="^(daily|weekly|monthly|all)$"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    多维度排行榜
    dimension: points | streak | mastery | quiz_score
    period: daily | weekly | monthly | all
    """
    now = datetime.now(timezone.utc)

    if period == "daily":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "weekly":
        start = now - timedelta(days=now.weekday())
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "monthly":
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        start = None

    results = []

    if dimension == "points":
        # 基于积分表
        query = db.query(PointsModel).order_by(PointsModel.total_points.desc())
        if period == "daily":
            query = db.query(PointsModel).order_by(PointsModel.daily_points.desc())
        elif period == "weekly":
            query = db.query(PointsModel).order_by(PointsModel.weekly_points.desc())

        rows = query.limit(limit).all()
        for i, row in enumerate(rows):
            score = row.total_points
            if period == "daily":
                score = row.daily_points
            elif period == "weekly":
                score = row.weekly_points
            results.append({
                "student_id": row.student_id,
                "score": score,
                "rank": i + 1,
            })

    elif dimension == "streak":
        # 基于学习记录计算连续天数
        all_students = db.query(
            LearningRecordModel.student_id
        ).distinct().all()

        streak_data = []
        for (sid,) in all_students:
            records = db.query(LearningRecordModel).filter(
                LearningRecordModel.student_id == sid,
            ).all()
            dates = set()
            for r in records:
                if r.created_at:
                    dates.add(r.created_at.strftime("%Y-%m-%d"))
            sorted_dates = sorted(dates, reverse=True)
            streak = 0
            for j, d in enumerate(sorted_dates):
                expected = (now.date() - timedelta(days=j)).isoformat()
                if d == expected:
                    streak += 1
                else:
                    break
            if streak > 0:
                streak_data.append({"student_id": sid, "score": streak})

        streak_data.sort(key=lambda x: x["score"], reverse=True)
        for i, item in enumerate(streak_data[:limit]):
            results.append({**item, "rank": i + 1})

    elif dimension == "mastery":
        # 基于掌握的知识点数
        all_students = db.query(
            LearningRecordModel.student_id
        ).distinct().all()

        mastery_data = []
        for (sid,) in all_students:
            query_filter = [LearningRecordModel.student_id == sid]
            if start:
                query_filter.append(LearningRecordModel.created_at >= start)
            records = db.query(LearningRecordModel).filter(*query_filter).all()
            completed = set()
            for r in records:
                if r.action == "complete" or _safe_float(r.progress) >= 1.0:
                    completed.add(r.kp_id)
            if completed:
                mastery_data.append({"student_id": sid, "score": len(completed)})

        mastery_data.sort(key=lambda x: x["score"], reverse=True)
        for i, item in enumerate(mastery_data[:limit]):
            results.append({**item, "rank": i + 1})

    elif dimension == "quiz_score":
        # 基于测验均分
        all_students = db.query(
            QuizResultModel.student_id
        ).distinct().all()

        score_data = []
        for (sid,) in all_students:
            query_filter = [QuizResultModel.student_id == sid]
            if start:
                query_filter.append(QuizResultModel.created_at >= start)
            quizzes = db.query(QuizResultModel).filter(*query_filter).all()
            if quizzes:
                avg = sum(q.score or 0 for q in quizzes) / len(quizzes)
                score_data.append({"student_id": sid, "score": round(avg, 1)})

        score_data.sort(key=lambda x: x["score"], reverse=True)
        for i, item in enumerate(score_data[:limit]):
            results.append({**item, "rank": i + 1})
    else:
        return {"status": "error", "message": f"未知维度: {dimension}"}

    # 补充用户名
    from ..models.user import UserModel
    for item in results:
        user = db.query(UserModel).filter(
            UserModel.student_id == item["student_id"]
        ).first()
        item["username"] = user.username if user else item["student_id"]

    return {
        "status": "success",
        "data": {
            "dimension": dimension,
            "period": period,
            "entries": results,
        },
    }
