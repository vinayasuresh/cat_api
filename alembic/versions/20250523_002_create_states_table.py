"""create states table

Revision ID: 20250523002
Revises: 20250523001
Create Date: 2025-05-23 00:02:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision = '20250523002'
down_revision = '20250523001'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'states',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(10), nullable=False),
        sa.Column('fips', sa.String(10), nullable=True, unique=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('status', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=func.now(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'])
    )
    op.create_index(op.f('ix_states_id'), 'states', ['id'], unique=False)
    op.create_index(op.f('ix_states_code'), 'states', ['code'], unique=True)
    op.create_index(op.f('ix_states_fips'), 'states', ['fips'], unique=True)


def downgrade():
    op.drop_index(op.f('ix_states_code'), table_name='states')
    op.drop_index(op.f('ix_states_id'), table_name='states')
    op.drop_index(op.f('ix_states_fips'), table_name='states')
    op.drop_table('states')
