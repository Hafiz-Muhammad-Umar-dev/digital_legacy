
"""add users and refresh_tokens

Revision ID: 652f866f9adf
Revises: dcc390ab5361
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "652f866f9adf"
down_revision: Union[str, Sequence[str], None] = "dcc390ab5361"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # This migration should not modify existing media_assets columns.
    # Those type changes were unrelated to the intended auth migration.
    pass


def downgrade() -> None:
    pass
