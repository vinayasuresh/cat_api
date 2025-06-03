"""create zipcodes table

Revision ID: 20250523004
Revises: 20250523003
Create Date: 2025-05-23 00:04:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision = '20250523004'
down_revision = '20250523003'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'zipcodes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(10), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('zone_county_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=func.now(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['zone_county_id'], ['zones_counties.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'])
    )
    op.create_index(op.f('ix_zipcodes_id'), 'zipcodes', ['id'], unique=False)
    op.create_index(op.f('ix_zipcodes_code'), 'zipcodes', ['code'], unique=True)


def downgrade():
    op.drop_index(op.f('ix_zipcodes_code'), table_name='zipcodes')
    op.drop_index(op.f('ix_zipcodes_id'), table_name='zipcodes')
    op.drop_table('zipcodes')
