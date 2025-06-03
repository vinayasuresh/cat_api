"""create policyholders table

Revision ID: 20250523008
Revises: 20250523007
Create Date: 2025-05-23 00:08:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision = '20250523008'
down_revision = '20250523007'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'policyholders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('policy_id', sa.String(50), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('zipcode_id', sa.Integer(), nullable=False),
        sa.Column('claims', sa.Integer(), nullable=True, default=0),
        sa.Column('premium', sa.Float(), nullable=True, default=0.0),
        sa.Column('state_id', sa.Integer(), nullable=True),
        sa.Column('county_id', sa.Integer(), nullable=True),
        sa.Column('address', sa.String(255), nullable=True),
        sa.Column('email', sa.String(100), nullable=True),
        sa.Column('phoneno', sa.String(20), nullable=True),
        sa.Column('status', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=func.now(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['zipcode_id'], ['zipcodes.id']),
        sa.ForeignKeyConstraint(['state_id'], ['states.id']),
        sa.ForeignKeyConstraint(['county_id'], ['zones_counties.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'])
    )
    op.create_index(op.f('ix_policyholders_id'), 'policyholders', ['id'], unique=False)
    op.create_index(op.f('ix_policyholders_policy_id'), 'policyholders', ['policy_id'], unique=True)


def downgrade():
    op.drop_index(op.f('ix_policyholders_policy_id'), table_name='policyholders')
    op.drop_index(op.f('ix_policyholders_id'), table_name='policyholders')
    op.drop_table('policyholders')
