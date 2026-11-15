"""personas owner_id not null

Revision ID: 9e7a9377a92e
Revises: 4da2f360cbbf
Create Date: 2026-10-18 00:36:53.815280

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9e7a9377a92e'
down_revision: Union[str, Sequence[str], None] = '4da2f360cbbf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "personas", "owner_id",
        existing_type=sa.CHAR(36),
        nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "personas", "owner_id",
        existing_type=sa.CHAR(36),
        nullable=True,
    )