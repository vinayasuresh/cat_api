"""create alert_affected_areas table

Revision ID: 20250523011
Revises: 20250523010
Create Date: 2025-05-23 00:11:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision = '20250523011'
down_revision = '20250523010'
branch_labels = None
depends_on = None


def upgrade():
    region_type = sa.Enum('ZONE', 'COUNTY', 'ZIPCODE', name='regiontype_alert')
    op.create_table(
        'alert_affected_areas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('alert_id', sa.Integer(), nullable=False),
        sa.Column('zone_county_id', sa.Integer(), nullable=True),
        sa.Column('zipcode_id', sa.Integer(), nullable=True),
        sa.Column('region_type', region_type, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['alert_id'], ['alerts.id']),
        sa.ForeignKeyConstraint(['zone_county_id'], ['zones_counties.id']),
        sa.ForeignKeyConstraint(['zipcode_id'], ['zipcodes.id'])
    )
    op.create_index(op.f('ix_alert_affected_areas_id'), 'alert_affected_areas', ['id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_alert_affected_areas_id'), table_name='alert_affected_areas')
    op.drop_table('alert_affected_areas')
    op.execute('DROP TYPE regiontype_alert')
