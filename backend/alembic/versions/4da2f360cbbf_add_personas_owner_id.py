
"""add personas owner_id

Revision ID: 4da2f360cbbf
Revises: 115a310a1f57
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision: str = "4da2f360cbbf"
down_revision: Union[str, Sequence[str], None] = "115a310a1f57"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "memories",
        sa.Column("status", sa.String(20), nullable=False,
                  server_default="pending_review"),
    )
    op.add_column("memories", sa.Column("original_content", sa.Text(), nullable=True))
    op.add_column("memories", sa.Column("reviewed_at", sa.DateTime(), nullable=True))

    # Backfill: video se nikli hui memories pending rahengi, baqi (manual) approved
    op.execute(
        "UPDATE memories SET status = 'approved', verified = 1, "
        "reviewed_at = NOW() WHERE source NOT LIKE 'video_transcript:%'"
    )

    op.create_index(
        "ix_memories_persona_status", "memories", ["persona_id", "status"]
    )


def downgrade() -> None:
    op.drop_index("ix_memories_persona_status", table_name="memories")
    op.drop_column("memories", "reviewed_at")
    op.drop_column("memories", "original_content")
    op.drop_column("memories", "status")