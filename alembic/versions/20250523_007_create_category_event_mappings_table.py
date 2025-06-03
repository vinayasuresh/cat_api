"""create category_event_mappings table

Revision ID: 20250523007
Revises: 20250523006
Create Date: 2025-05-23 00:07:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision = '20250523007'
down_revision = '20250523006'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'category_event_mappings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE')
    )
    op.create_index(op.f('ix_category_event_mappings_id'), 'category_event_mappings', ['id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_category_event_mappings_id'), table_name='category_event_mappings')
    op.drop_table('category_event_mappings')
