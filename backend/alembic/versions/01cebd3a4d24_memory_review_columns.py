"""memory review columns

Revision ID: 01cebd3a4d24
Revises: fd3ac9451823
Create Date: 2026-10-18 01:21:44.554573

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '01cebd3a4d24'
down_revision: Union[str, Sequence[str], None] = 'fd3ac9451823'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


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