"""personas owner_id not null

Revision ID: 115a310a1f57
Revises: 652f866f9adf
Create Date: 2026-10-18 00:19:22.308017

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '115a310a1f57'
down_revision: Union[str, Sequence[str], None] = '652f866f9adf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
