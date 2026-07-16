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
    # 先将索引改为唯一约束，防止同 student_id+title 重复创建笔记
    op.drop_index(op.f('ix_kb_notes_student_title'), table_name='kb_notes')
    op.create_unique_constraint('uq_kb_notes_student_title', 'kb_notes', ['student_id', 'title'])


def downgrade() -> None:
    op.drop_constraint('uq_kb_notes_student_title', 'kb_notes', type_='unique')
    op.create_index(op.f('ix_kb_notes_student_title'), 'kb_notes', ['student_id', 'title'], unique=False)
