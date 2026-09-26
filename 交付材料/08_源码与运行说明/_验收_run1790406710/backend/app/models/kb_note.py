"""
知识库模型 - 笔记和文件夹
"""
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


class KBFolderModel(Base):
    """知识库文件夹"""
    __tablename__ = "kb_folders"

    folder_id = Column(String(64), primary_key=True, index=True)
    student_id = Column(String(64), index=True, nullable=False)
    name = Column(String(255), nullable=False)
    parent_id = Column(String(64), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index("ix_kb_folders_student_parent", "student_id", "parent_id"),
    )


class KBNoteModel(Base):
    """知识库笔记"""
    __tablename__ = "kb_notes"

    note_id = Column(String(64), primary_key=True, index=True)
    student_id = Column(String(64), index=True, nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, default="")
    folder_id = Column(String(64), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("student_id", "title", name="uq_kb_notes_student_title"),
        Index("ix_kb_notes_student_folder", "student_id", "folder_id"),
    )
