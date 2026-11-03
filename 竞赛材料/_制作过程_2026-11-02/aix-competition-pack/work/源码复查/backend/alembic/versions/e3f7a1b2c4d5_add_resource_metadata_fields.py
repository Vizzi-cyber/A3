"""Add metadata fields to resource_tasks

Revision ID: e3f7a1b2c4d5
Revises: 8856cb755504
Create Date: 2026-06-22

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'e3f7a1b2c4d5'
down_revision: Union[str, None] = '84ffd4bbb01d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('resource_tasks', sa.Column('title', sa.String(200), server_default=''))
    op.add_column('resource_tasks', sa.Column('resource_type', sa.String(32), server_default='document'))
    op.add_column('resource_tasks', sa.Column('subject', sa.String(50), server_default='Python'))
    op.add_column('resource_tasks', sa.Column('difficulty', sa.String(20), server_default='medium'))


def downgrade() -> None:
    op.drop_column('resource_tasks', 'title')
    op.drop_column('resource_tasks', 'resource_type')
    op.drop_column('resource_tasks', 'subject')
    op.drop_column('resource_tasks', 'difficulty')
