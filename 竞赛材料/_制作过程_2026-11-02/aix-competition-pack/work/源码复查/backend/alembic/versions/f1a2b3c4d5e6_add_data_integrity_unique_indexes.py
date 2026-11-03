"""add data integrity unique indexes

Revision ID: f1a2b3c4d5e6
Revises: e5f22346d72c
Create Date: 2026-09-02

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f1a2b3c4d5e6"
down_revision: Union[str, None] = "e5f22346d72c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _remove_duplicate_rows(table: str, columns: list[str]) -> None:
    """Keep the oldest row in each logical group before adding a unique index."""
    connection = op.get_bind()
    quoted_table = connection.dialect.identifier_preparer.quote(table)
    quoted_columns = [connection.dialect.identifier_preparer.quote(column) for column in columns]
    group_by = ", ".join(quoted_columns)
    connection.execute(sa.text(
        f"DELETE FROM {quoted_table} WHERE rowid NOT IN "
        f"(SELECT MIN(rowid) FROM {quoted_table} GROUP BY {group_by})"
    ))


def upgrade() -> None:
    # Existing deployments received these indexes as non-unique in early revisions.
    # Deduplicate legacy data first so the migration is safe on real demo databases.
    _remove_duplicate_rows("game_achievements", ["student_id", "achievement_id"])
    _remove_duplicate_rows("game_tasks", ["student_id", "task_id"])
    _remove_duplicate_rows("learning_logs", ["student_id", "date"])

    op.drop_index("ix_achievements_student_achievement", table_name="game_achievements")
    op.create_index(
        "ix_achievements_student_achievement",
        "game_achievements",
        ["student_id", "achievement_id"],
        unique=True,
    )
    op.drop_index("ix_tasks_student_task", table_name="game_tasks")
    op.create_index("ix_tasks_student_task", "game_tasks", ["student_id", "task_id"], unique=True)
    op.drop_index("ix_learning_logs_student_date", table_name="learning_logs")
    op.create_index(
        "ix_learning_logs_student_date",
        "learning_logs",
        ["student_id", "date"],
        unique=True,
    )
    op.create_index(
        "uq_quiz_results_experiment_student_phase",
        "quiz_results",
        ["experiment_id", "student_id", "assessment_phase"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("uq_quiz_results_experiment_student_phase", table_name="quiz_results")
    op.drop_index("ix_learning_logs_student_date", table_name="learning_logs")
    op.create_index("ix_learning_logs_student_date", "learning_logs", ["student_id", "date"], unique=False)
    op.drop_index("ix_tasks_student_task", table_name="game_tasks")
    op.create_index("ix_tasks_student_task", "game_tasks", ["student_id", "task_id"], unique=False)
    op.drop_index("ix_achievements_student_achievement", table_name="game_achievements")
    op.create_index(
        "ix_achievements_student_achievement",
        "game_achievements",
        ["student_id", "achievement_id"],
        unique=False,
    )
