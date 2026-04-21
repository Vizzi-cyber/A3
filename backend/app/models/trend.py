"""
学习趋势与评估数据 ORM 模型
"""
from sqlalchemy import Column, String, DateTime, JSON, Float, Integer
from sqlalchemy.sql import func

from .database import Base


class TrendDataModel(Base):
    """学生趋势数据表"""
    __tablename__ = "student_trends"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(64), index=True, nullable=False)
    date = Column(String(10), index=True, nullable=False)  # YYYY-MM-DD

    # 5大维度得分
    mastery_trend = Column(Float, default=0.0)      # 知识掌握度趋势（40%）
    speed_ratio = Column(Float, default=0.0)        # 学习速度比例（20%）
    time_efficiency = Column(Float, default=0.0)    # 学习时间效率（15%）
    weakness_priority = Column(Float, default=0.0)  # 薄弱点优先级得分（15%）
    stability = Column(Float, default=0.0)          # 连续学习稳定性（10%）

    # 综合趋势因子与状态
    trend_factor = Column(Float, default=0.0)       # -1.0 ~ 1.0
    trend_state = Column(String(16), default="stable")  # growth / decline / warning / stable

    # 预测与建议
    predicted_mastery_3d = Column(Float, default=0.0)
    intervention = Column(String(256), nullable=True)
    details = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
