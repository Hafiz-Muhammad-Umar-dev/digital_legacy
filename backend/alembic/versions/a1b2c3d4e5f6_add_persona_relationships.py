"""add persona relationships

Revision ID: a1b2c3d4e5f6
Revises: b51b8fe368cc
Create Date: 2026-11-15 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'b51b8fe368cc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'persona_relationships',
        sa.Column('id', sa.CHAR(length=36), nullable=False),
        sa.Column('persona_id', sa.CHAR(length=36), nullable=False),
        sa.Column('member_name', sa.String(length=150), nullable=False),
        sa.Column('relationship_type', sa.String(length=80), nullable=False),
        sa.Column('preferred_name', sa.String(length=150), nullable=True),
        sa.Column('biographical_notes', sa.Text(), nullable=True),
        sa.Column('linked_user_id', sa.CHAR(length=36), nullable=True),
        sa.Column('verification_status', sa.String(length=30), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['persona_id'], ['personas.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['linked_user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_persona_relationships_persona_id'), 'persona_relationships', ['persona_id'], unique=False)
    op.create_index(op.f('ix_persona_relationships_linked_user_id'), 'persona_relationships', ['linked_user_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_persona_relationships_linked_user_id'), table_name='persona_relationships')
    op.drop_index(op.f('ix_persona_relationships_persona_id'), table_name='persona_relationships')
    op.drop_table('persona_relationships')
