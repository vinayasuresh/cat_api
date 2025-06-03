"""create zones_counties table

Revision ID: 20250523003
Revises: 20250523002
Create Date: 2025-05-23 00:03:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision = '20250523003'
down_revision = '20250523002'
branch_labels = None
depends_on = None


def upgrade():
    region_type = sa.Enum('ZONE', 'COUNTY', name='regiontype')
    op.create_table(
        'zones_counties',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(10), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('fips', sa.String(5), nullable=False),
        sa.Column('type', region_type, nullable=False),
        sa.Column('state_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=func.now(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['state_id'], ['states.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'])
    )
    op.create_index(op.f('ix_zones_counties_id'), 'zones_counties', ['id'], unique=False)
    op.create_index(op.f('ix_zones_counties_code'), 'zones_counties', ['code'], unique=True)


def downgrade():
    op.drop_index(op.f('ix_zones_counties_code'), table_name='zones_counties')
    op.drop_index(op.f('ix_zones_counties_id'), table_name='zones_counties')
    op.drop_table('zones_counties')
    op.execute('DROP TYPE regiontype')
