"""memory review status

Revision ID: fd3ac9451823
Revises: 9e7a9377a92e
Create Date: 2026-10-18 01:09:35.331367

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fd3ac9451823'
down_revision: Union[str, Sequence[str], None] = '9e7a9377a92e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
