"""
游戏化服务层
统一管理积分、成就、排行榜逻辑
"""
from datetime import date, datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from ..models.gamification import PointsModel, AchievementModel, LeaderboardModel


def ensure_points(db: Session, student_id: str) -> PointsModel:
    """确保积分记录存在，并自动重置每日/每周积分"""
    points = db.query(PointsModel).filter(PointsModel.student_id == student_id).first()
    if not points:
        points = PointsModel(student_id=student_id, total_points=0, daily_points=0, weekly_points=0)
        db.add(points)
        db.flush()
    # 每日/每周积分自动重置
    now = datetime.now(timezone.utc)
    updated = points.updated_at
    if updated:
        if updated.date() < now.date():
            points.daily_points = 0
        if updated.isocalendar()[1] != now.isocalendar()[1] or updated.year != now.year:
            points.weekly_points = 0
    return points


def award_points(db: Session, student_id: str, amount: int, reason: str = "") -> int:
    """增加积分并同步排行榜（调用方负责 commit）"""
    points = ensure_points(db, student_id)
    points.total_points += amount
    points.daily_points += amount
    points.weekly_points += amount
    # 同步排行榜
    sync_leaderboard(db, student_id, points)
    return points.total_points


def sync_leaderboard(db: Session, student_id: str, points: PointsModel):
    """同步排行榜数据"""
    for period in ("daily", "weekly", "monthly"):
        row = db.query(LeaderboardModel).filter(
            LeaderboardModel.student_id == student_id,
            LeaderboardModel.period == period,
        ).first()
        score = (
            points.daily_points if period == "daily"
            else points.weekly_points if period == "weekly"
            else points.total_points
        )
        if row:
            row.score = score
        else:
            db.add(LeaderboardModel(student_id=student_id, period=period, score=score))


def maybe_unlock_achievement(
    db: Session,
    student_id: str,
    achievement_id: str,
    name: str,
    description: str,
    icon: str = "trophy",
) -> bool:
    """解锁成就，如果已存在则返回 False"""
    existing = db.query(AchievementModel).filter(
        AchievementModel.student_id == student_id,
        AchievementModel.achievement_id == achievement_id,
    ).first()
    if existing:
        return False
    ach = AchievementModel(
        student_id=student_id,
        achievement_id=achievement_id,
        name=name,
        description=description,
        icon=icon,
    )
    db.add(ach)
    return True


# ---------- 进阶成就（与前端徽章墙按 achievement_id 对齐） ----------

def check_progress_achievements(db: Session, student_id: str) -> None:
    """基于学习行为统计解锁进阶成就（同一事务内，调用方负责 commit）"""
    from sqlalchemy import func as sa_func

    from ..models.knowledge import LearningRecordModel

    records = db.query(LearningRecordModel).filter(
        LearningRecordModel.student_id == student_id
    )
    total = records.count()
    if total == 0:
        return

    # 百炼成钢：累计20次学习行为
    if total >= 20:
        maybe_unlock_achievement(
            db, student_id, "practice_20", "百炼成钢", "累计20次学习行为", "thunderbolt"
        )

    # 博学多才：完成10个不同知识点
    completed_kps = (
        db.query(LearningRecordModel.kp_id)
        .filter(
            LearningRecordModel.student_id == student_id,
            LearningRecordModel.action == "complete",
        )
        .distinct()
        .count()
    )
    if completed_kps >= 10:
        maybe_unlock_achievement(
            db, student_id, "complete_10", "博学多才", "完成10个不同知识点的学习", "book"
        )

    # 勤学不辍：连续打卡7天（按有学习记录的自然日连续计算）
    # SQLite 的 func.date() 返回字符串，PostgreSQL 返回 date —— 统一归一化
    normalized = set()
    for (d,) in db.query(sa_func.date(LearningRecordModel.created_at)).filter(
        LearningRecordModel.student_id == student_id
    ):
        if isinstance(d, datetime):
            normalized.add(d.date())
        elif isinstance(d, date):
            normalized.add(d)
        elif isinstance(d, str):
            normalized.add(date.fromisoformat(d[:10]))
    dates = sorted(normalized)
    if dates:
        today = datetime.now(timezone.utc).astimezone().date()
        if (today - dates[-1]).days <= 1:  # 今天或昨天有记录才算连续
            streak = 1
            for i in range(len(dates) - 2, -1, -1):
                if (dates[i + 1] - dates[i]).days == 1:
                    streak += 1
                else:
                    break
            if streak >= 7:
                maybe_unlock_achievement(
                    db, student_id, "streak_7", "勤学不辍", "连续打卡7天", "fire"
                )
    return
