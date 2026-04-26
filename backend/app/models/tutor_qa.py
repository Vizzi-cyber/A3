"""
智能辅导问答记录 ORM 模型
持久化存储学生与AI辅导助手的问答历史
"""
from sqlalchemy import Column, String, DateTime, Text, JSON, Integer, Float, Boolean
from sqlalchemy.sql import func

from .database import Base


class TutorQAModel(Base):
    """辅导问答记录表"""
    __tablename__ = "tutor_qa_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(64), index=True, nullable=False)
    session_id = Column(String(128), index=True, nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    # 支持多模态输入时存储原始输入结构
    question_meta = Column(JSON, nullable=True)
    # 学生画像快照（记录问答时的画像状态）
    profile_snapshot = Column(JSON, nullable=True)
    # 回答类型: explanation / hint / encouragement / blocked
    response_type = Column(String(32), default="explanation")
    # 是否包含敏感内容被拦截
    blocked = Column(Boolean, default=False)
    block_reason = Column(Text, nullable=True)
    # 使用的LLM提供商
    llm_provider = Column(String(32), nullable=True)
    # 评分/反馈（学生可对回答点赞/点踩）
    feedback = Column(String(16), nullable=True)  # like / dislike
    created_at = Column(DateTime(timezone=True), server_default=func.now())
