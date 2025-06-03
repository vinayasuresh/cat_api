"""create alerts table

Revision ID: 20250523010
Revises: 20250523009
Create Date: 2025-05-23 00:10:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision = '20250523010'
down_revision = '20250523009'
branch_labels = None
depends_on = None


def upgrade():
    alert_status = sa.Enum('NEW', 'READ', 'ARCHIVED', name='alertstatus')
    alert_severity = sa.Enum('LOW', 'MEDIUM', 'HIGH', name='alertseverity')

    op.create_table(
        'alerts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('status', alert_status, nullable=True, default='new'),
        sa.Column('severity', alert_severity, nullable=False),
        sa.Column('state_id', sa.Integer(), nullable=True),
        sa.Column('source', sa.String(), nullable=True),
        sa.Column('event_type', sa.String(), nullable=True),
        sa.Column('external_id', sa.String(), nullable=True),
        sa.Column('event_timestamp', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=func.now(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['state_id'], ['states.id'])
    )
    op.create_index(op.f('ix_alerts_id'), 'alerts', ['id'], unique=False)
    op.create_index(op.f('ix_alerts_title'), 'alerts', ['title'], unique=False)
    op.create_index(op.f('ix_alerts_event_type'), 'alerts', ['event_type'], unique=False)
    op.create_index(op.f('ix_alerts_external_id'), 'alerts', ['external_id'], unique=True)


def downgrade():
    op.drop_index(op.f('ix_alerts_external_id'), table_name='alerts')
    op.drop_index(op.f('ix_alerts_event_type'), table_name='alerts')
    op.drop_index(op.f('ix_alerts_title'), table_name='alerts')
    op.drop_index(op.f('ix_alerts_id'), table_name='alerts')
    op.drop_table('alerts')
    op.execute('DROP TYPE alertstatus')
    op.execute('DROP TYPE alertseverity')
