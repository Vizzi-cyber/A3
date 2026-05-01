"""
系统监控 ORM 模型
"""
from sqlalchemy import Column, String, DateTime, JSON, Integer, Float, Text, Boolean, Index
from sqlalchemy.sql import func

from .database import Base


class ApiMonitorModel(Base):
    """API接口监控表"""
    __tablename__ = "api_monitor"

    id = Column(Integer, primary_key=True, autoincrement=True)
    endpoint = Column(String(256), nullable=False)
    method = Column(String(16), nullable=False)
    status_code = Column(Integer, default=200)
    duration_ms = Column(Float, default=0.0)
    student_id = Column(String(64), nullable=True)
    error_msg = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_api_monitor_created_at", "created_at"),
    )


class LlmCallModel(Base):
    """大模型调用监控表"""
    __tablename__ = "llm_calls"

    id = Column(Integer, primary_key=True, autoincrement=True)
    provider = Column(String(32), nullable=False)
    model = Column(String(64), nullable=True)
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    duration_ms = Column(Float, default=0.0)
    success = Column(Boolean, default=True)
    error_msg = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_llm_calls_created_at", "created_at"),
    )


class SystemHealthModel(Base):
    """系统健康监控表"""
    __tablename__ = "system_health"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cpu_percent = Column(Float, default=0.0)
    memory_percent = Column(Float, default=0.0)
    disk_percent = Column(Float, default=0.0)
    active_connections = Column(Integer, default=0)
    queue_size = Column(Integer, default=0)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_system_health_recorded_at", "recorded_at"),
    )
