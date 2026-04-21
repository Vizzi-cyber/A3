"""
游戏化学习 ORM 模型
"""
from sqlalchemy import Column, String, DateTime, JSON, Integer, Float, Boolean
from sqlalchemy.sql import func

from .database import Base


class PointsModel(Base):
    """积分表"""
    __tablename__ = "game_points"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(64), index=True, nullable=False)
    total_points = Column(Integer, default=0)
    daily_points = Column(Integer, default=0)
    weekly_points = Column(Integer, default=0)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AchievementModel(Base):
    """成就徽章表（按学生记录已解锁）"""
    __tablename__ = "game_achievements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(64), index=True, nullable=False)
    achievement_id = Column(String(64), nullable=False)
    name = Column(String(128), nullable=False)
    description = Column(String(512), nullable=True)
    icon = Column(String(256), nullable=True)
    unlocked_at = Column(DateTime(timezone=True), server_default=func.now())


class TaskModel(Base):
    """学习任务与挑战任务表"""
    __tablename__ = "game_tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(64), index=True, nullable=False)
    task_id = Column(String(64), nullable=False)
    title = Column(String(256), nullable=False)
    description = Column(String(512), nullable=True)
    task_type = Column(String(32), default="daily")  # daily / weekly / challenge
    reward_points = Column(Integer, default=0)
    progress = Column(Float, default=0.0)  # 0.0 ~ 1.0
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    deadline = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class LeaderboardModel(Base):
    """排行榜快照表"""
    __tablename__ = "leaderboard"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(64), index=True, nullable=False)
    period = Column(String(16), default="weekly")  # daily / weekly / monthly
    score = Column(Integer, default=0)
    rank = Column(Integer, default=0)
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
