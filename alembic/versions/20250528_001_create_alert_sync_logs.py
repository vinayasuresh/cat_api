"""create alert sync logs

Revision ID: 20250528001
Revises: 20250523011
Create Date: 2025-05-28 00:01:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision = '20250528001'
down_revision = '20250523011'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'alert_sync_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('total_alerts', sa.Integer(), nullable=False),
        sa.Column('processed_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('ignored_by_state', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('ignored_by_missing_data', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('error_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('missing_states', sa.JSON(), nullable=True),
        # Zipcode processing summary fields
        sa.Column('processed_same_codes', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('skipped_same_codes', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('found_zipcodes', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_zipcode_mappings', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('used_zipcode_mappings', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('sync_timestamp', sa.DateTime(timezone=True), server_default=func.now(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_alert_sync_logs_id'), 'alert_sync_logs', ['id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_alert_sync_logs_id'), table_name='alert_sync_logs')
    op.drop_table('alert_sync_logs')
