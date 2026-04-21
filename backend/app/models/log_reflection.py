"""
学习日志与自我反思 ORM 模型
"""
from sqlalchemy import Column, String, DateTime, JSON, Integer, Text, Float
from sqlalchemy.sql import func

from .database import Base


class LearningLogModel(Base):
    """学习日志自动记录表"""
    __tablename__ = "learning_logs"

    log_id = Column(String(64), primary_key=True, index=True)
    student_id = Column(String(64), index=True, nullable=False)
    date = Column(String(10), index=True, nullable=False)  # YYYY-MM-DD

    # 当日学习概览
    total_duration = Column(Integer, default=0)  # 秒
    kp_count = Column(Integer, default=0)
    quiz_count = Column(Integer, default=0)
    avg_score = Column(Float, default=0.0)
    mistakes = Column(JSON, default=list)
    path_progress = Column(Float, default=0.0)
    completed_tasks = Column(JSON, default=list)

    # 时间线明细
    timeline = Column(JSON, default=list)  # [{time, action, kp_id, duration}]
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ReflectionModel(Base):
    """反思记录表"""
    __tablename__ = "reflections"

    reflection_id = Column(String(64), primary_key=True, index=True)
    student_id = Column(String(64), index=True, nullable=False)
    date = Column(String(10), index=True, nullable=False)
    content = Column(Text, nullable=False)
    mood = Column(String(32), default="neutral")  # happy / neutral / frustrated / excited
    tags = Column(JSON, default=list)
    ai_feedback = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
