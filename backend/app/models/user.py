"""
用户认证 ORM 模型
"""
from sqlalchemy import Column, String, DateTime, Boolean, Integer
from sqlalchemy.sql import func

from .database import Base


class UserModel(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(String(64), unique=True, index=True, nullable=False)
    username = Column(String(128), nullable=False)
    email = Column(String(128), unique=True, nullable=True)
    hashed_password = Column(String(256), nullable=True)
    is_active = Column(Boolean, default=True)
    role = Column(String(32), default="student")  # student / teacher / admin
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
