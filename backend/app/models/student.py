"""
学生画像 ORM 模型
"""
from sqlalchemy import Column, String, DateTime, Text, JSON
from sqlalchemy.sql import func

from .database import Base


class StudentProfileModel(Base):
    """学生画像表"""
    __tablename__ = "student_profiles"

    student_id = Column(String(64), primary_key=True, index=True)
    knowledge_base = Column(JSON, default=dict)
    cognitive_style = Column(JSON, default=dict)
    weak_areas = Column(JSON, default=list)
    error_patterns = Column(JSON, default=list)
    learning_goals = Column(JSON, default=list)
    interest_areas = Column(JSON, default=list)
    learning_tempo = Column(JSON, default=dict)
    practical_preferences = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
