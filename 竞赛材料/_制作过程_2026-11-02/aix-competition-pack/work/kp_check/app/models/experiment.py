"""
实验行为日志模型
记录电路仿真、故障诊断、STM32 仿真等实验实训行为，
支撑试点数据分析中的"实验参与度"维度（AIC AI+学科交叉赛道）
"""
from sqlalchemy import Column, String, Integer, JSON, DateTime, Index, Text, func
from .database import Base


class ExperimentBatchModel(Base):
    """正式试点实验批次。"""

    __tablename__ = "experiment_batches"

    experiment_id = Column(String(64), primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(32), nullable=False, default="draft")
    intervention_type = Column(String(64), nullable=False, default="ai_learning_path")
    seed = Column(Integer, nullable=True)
    config = Column(JSON, nullable=False, default=dict)
    created_by = Column(String(64), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (Index("ix_experiment_batches_status", "status"),)


class ExperimentAssignmentModel(Base):
    """正式实验中的学生分组。"""

    __tablename__ = "experiment_assignments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    experiment_id = Column(String(64), nullable=False, index=True)
    student_id = Column(String(64), nullable=False, index=True)
    group_name = Column(String(16), nullable=False)
    allocation_method = Column(String(32), nullable=False, default="random")
    allocation_seed = Column(Integer, nullable=True)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("uq_experiment_assignment_student", "experiment_id", "student_id", unique=True),
        Index("ix_experiment_assignment_group", "experiment_id", "group_name"),
    )


class ExperimentFeedbackModel(Base):
    """正式实验问卷反馈。"""

    __tablename__ = "experiment_feedback"

    id = Column(Integer, primary_key=True, autoincrement=True)
    experiment_id = Column(String(64), nullable=False, index=True)
    student_id = Column(String(64), nullable=False, index=True)
    questionnaire_version = Column(String(64), nullable=False)
    answers = Column(JSON, nullable=False, default=dict)
    comment = Column(Text, nullable=True)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index(
            "uq_experiment_feedback_version",
            "experiment_id", "student_id", "questionnaire_version", unique=True,
        ),
    )


class ExperimentLogModel(Base):
    """实验行为日志表。"""

    __tablename__ = "experiment_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(64), index=True, nullable=False)
    experiment_id = Column(String(64), nullable=True, index=True)
    experiment_type = Column(String(64), nullable=False)  # circuit_simulate / circuit_fault / stm32_simulate
    action = Column(String(64), default="run")               # run / diagnose / submit / complete
    detail = Column(JSON, default=dict)
    duration = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_experiment_student_type", "student_id", "experiment_type"),
        Index("ix_experiment_created", "created_at"),
        Index("ix_experiment_batch_created", "experiment_id", "created_at"),
    )
