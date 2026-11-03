"""
记忆卡片表（FSRS 间隔重复状态持久化）

存储每个 学生 × 知识点 的 FSRS 记忆卡片（Card.to_json() 序列化），
由 memory_scheduler.py 的 FSRSMemoryScheduler 读写。
"""
from sqlalchemy import Column, DateTime, Index, Integer, String, Text, func

from .database import Base


class MemoryCardModel(Base):
    """FSRS 记忆卡片表"""
    __tablename__ = "memory_cards"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(64), index=True, nullable=False)
    kp_id = Column(String(64), index=True, nullable=False)
    card_json = Column(Text, nullable=False, default="{}")  # fsrs Card.to_json()
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("ix_memory_student_kp", "student_id", "kp_id", unique=True),
    )
