"""add_unique_constraint_kb_notes_student_title

Revision ID: e5f22346d72c
Revises: e3f7a1b2c4d5
Create Date: 2026-07-16 17:14:58.952813

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'e5f22346d72c'
down_revision: Union[str, None] = 'e3f7a1b2c4d5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # SQLite 不支持直接创建表级唯一约束，使用唯一索引保持跨数据库兼容。
    # 清理历史重复笔记，仅保留每组最早的一条。
    connection = op.get_bind()
    connection.execute(sa.text(
        "DELETE FROM kb_notes WHERE rowid NOT IN "
        "(SELECT MIN(rowid) FROM kb_notes GROUP BY student_id, title)"
    ))
    inspector = sa.inspect(connection)
    if "ix_kb_notes_student_title" in {idx["name"] for idx in inspector.get_indexes("kb_notes")}:
        op.drop_index("ix_kb_notes_student_title", table_name="kb_notes")
    op.create_index(
        'uq_kb_notes_student_title', 'kb_notes', ['student_id', 'title'], unique=True
    )


def downgrade() -> None:
    op.drop_index('uq_kb_notes_student_title', table_name='kb_notes')
    op.create_index(op.f('ix_kb_notes_student_title'), 'kb_notes', ['student_id', 'title'], unique=False)
