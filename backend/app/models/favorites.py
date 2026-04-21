"""
收藏夹/书签 ORM 模型
"""
from sqlalchemy import Column, String, DateTime, Text, JSON
from sqlalchemy.sql import func

from .database import Base


class FavoriteModel(Base):
    """学生收藏资源表"""
    __tablename__ = "favorites"

    id = Column(String(64), primary_key=True, index=True)
    student_id = Column(String(64), index=True, nullable=False)
    title = Column(String(256), nullable=False)
    resource_type = Column(String(32), nullable=False)  # doc / video / code / tool / article
    url = Column(Text, nullable=True)
    meta = Column(JSON, default=dict)  # icon, color, description, tags 等
    created_at = Column(DateTime(timezone=True), server_default=func.now())
