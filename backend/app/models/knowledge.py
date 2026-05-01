"""
知识点与学习记录 ORM 模型
"""
from sqlalchemy import Column, String, DateTime, JSON, Float, Integer, ForeignKey, Text, Index
from sqlalchemy.sql import func

from .database import Base


class KnowledgePointModel(Base):
    """知识点表（支持DAG前置依赖，含课程内容）"""
    __tablename__ = "knowledge_points"

    kp_id = Column(String(64), primary_key=True, index=True)
    name = Column(String(256), nullable=False)
    subject = Column(String(64), nullable=False)
    difficulty = Column(Float, default=0.5)  # 0.0 ~ 1.0
    prerequisites = Column(JSON, default=list)  # 前置知识点ID列表
    description = Column(Text, nullable=True)
    tags = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 课程内容字段（替代硬编码 content_library）
    document = Column(Text, nullable=True)        # Markdown 图文讲义
    code_example = Column(Text, nullable=True)    # 代码示例
    questions = Column(JSON, nullable=True)       # 练习题列表
    mindmap = Column(JSON, nullable=True)         # 思维导图 JSON


class LearningRecordModel(Base):
    """学习记录表"""
    __tablename__ = "learning_records"

    record_id = Column(String(64), primary_key=True, index=True)
    student_id = Column(String(64), index=True, nullable=False)
    kp_id = Column(String(64), index=True, nullable=False)
    action = Column(String(64), nullable=False)  # watch / read / practice / review
    duration = Column(Integer, default=0)  # 学习时长（秒）
    progress = Column(Float, default=0.0)  # 0.0 ~ 1.0
    score = Column(Float, nullable=True)  # 练习得分
    meta = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_learning_records_student_action", "student_id", "action"),
    )


class QuizResultModel(Base):
    """测验结果表"""
    __tablename__ = "quiz_results"

    quiz_id = Column(String(64), primary_key=True, index=True)
    student_id = Column(String(64), index=True, nullable=False)
    kp_id = Column(String(64), index=True, nullable=False)
    total_questions = Column(Integer, default=0)
    correct_count = Column(Integer, default=0)
    score = Column(Float, default=0.0)  # 百分制
    weak_tags = Column(JSON, default=list)
    time_spent = Column(Integer, default=0)  # 用时（秒）
    answers = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_quiz_results_created_at", "created_at"),
    )
