"""
学科/课程元数据模型
支撑"AI+学科交叉"定位：每门课程明确所属学科领域与核心环节
"""
from sqlalchemy import Column, String, Text, JSON
from .database import Base


class CourseModel(Base):
    """学科课程元数据表"""

    __tablename__ = "courses"

    course_id = Column(String(64), primary_key=True)          # 课程标识，如 "C语言" / "电路分析" / "STM32嵌入式"
    name = Column(String(128), nullable=False)                # 课程名称
    discipline = Column(String(128), nullable=False)          # 所属学科领域（一级学科），如 "计算机科学与技术"
    core_phases = Column(JSON, default=list)                  # 覆盖的核心环节：教学实践/实验实训/自主学习
    description = Column(Text, default="")                    # 课程简介
    icon = Column(String(16), default="📘")                   # 前端展示图标
    color = Column(String(16), default="#1677ff")             # 前端图谱学科着色
    linked_courses = Column(JSON, default=list)               # 跨学科关联课程及说明（学科交叉定位）
    created_at = Column(String(64), default="")               # 创建时间占位（简单字符串，保持与现有模型风格一致）
