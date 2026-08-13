"""
实验行为日志模型
记录电路仿真、故障诊断、STM32 仿真等实验实训行为，
支撑试点数据分析中的"实验参与度"维度（AIC AI+学科交叉赛道）
"""
from sqlalchemy import Column, String, Integer, Float, JSON, DateTime, Index, func
from .database import Base


class ExperimentLogModel(Base):
    """实验行为日志表"""

    __tablename__ = "experiment_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(64), index=True, nullable=False)
    experiment_type = Column(String(64), nullable=False)  # circuit_simulate / circuit_fault / stm32_simulate
    action = Column(String(64), default="run")            # run / diagnose / submit / complete
    detail = Column(JSON, default=dict)                   # 实验详情（结果/耗时/选项等）
    duration = Column(Integer, default=0)                 # 耗时（秒）
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_experiment_student_type", "student_id", "experiment_type"),
        Index("ix_experiment_created", "created_at"),
    )
