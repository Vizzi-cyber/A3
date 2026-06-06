"""
路径调整日志 ORM 模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, JSON
from sqlalchemy.sql import func

from .database import Base


class PathAdjustmentLogModel(Base):
    """路径调整日志表"""
    __tablename__ = "path_adjustment_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(64), nullable=False, index=True)
    trigger_type = Column(String(32), nullable=False)  # onboarding | auto | manual
    trigger_source = Column(String(64), nullable=True)  # quiz_score_drop | reflection_keywords | tutor_frequency
    reason = Column(Text, nullable=True)
    old_path_snapshot = Column(JSON, nullable=True)
    new_path_snapshot = Column(JSON, nullable=True)
    confidence = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
