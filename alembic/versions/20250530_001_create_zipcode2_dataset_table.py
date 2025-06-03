"""create zipcode2_dataset table

Revision ID: 20250530001
Revises: 20250528001
Create Date: 2025-05-30 00:01:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision = '20250530001'
down_revision = '20250528001'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'zipcode2_dataset',
        sa.Column('zip_code', sa.String(), nullable=False),
        sa.Column('usps_city_name', sa.String(), nullable=True),
        sa.Column('usps_state_code', sa.String(), nullable=True),
        sa.Column('state_name', sa.String(), nullable=True),
        sa.Column('zcta', sa.Boolean(), nullable=True),
        sa.Column('zcta_parent', sa.String(), nullable=True),
        sa.Column('population', sa.Float(), nullable=True),
        sa.Column('density', sa.Float(), nullable=True),
        sa.Column('primary_county_code', sa.String(), nullable=True),
        sa.Column('primary_county_name', sa.String(), nullable=True),
        sa.Column('county_weights', sa.JSON(), nullable=True),
        sa.Column('county_names', sa.String(), nullable=True),
        sa.Column('county_codes', sa.String(), nullable=True),
        sa.Column('imprecise', sa.Boolean(), nullable=True),
        sa.Column('military', sa.Boolean(), nullable=True),
        sa.Column('timezone', sa.String(), nullable=True),
        sa.Column('geo_point', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('zip_code')
    )
    op.create_index(op.f('ix_zipcode2_dataset_zip_code'), 'zipcode2_dataset', ['zip_code'], unique=False)
    op.create_index(op.f('ix_zipcode2_dataset_usps_state_code'), 'zipcode2_dataset', ['usps_state_code'], unique=False)
    op.create_index(op.f('ix_zipcode2_dataset_state_name'), 'zipcode2_dataset', ['state_name'], unique=False)
    op.create_index(op.f('ix_zipcode2_dataset_primary_county_code'), 'zipcode2_dataset', ['primary_county_code'], unique=False)
    op.create_index(op.f('ix_zipcode2_dataset_county_codes'), 'zipcode2_dataset', ['county_codes'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_zipcode2_dataset_county_codes'), table_name='zipcode2_dataset')
    op.drop_index(op.f('ix_zipcode2_dataset_primary_county_code'), table_name='zipcode2_dataset')
    op.drop_index(op.f('ix_zipcode2_dataset_state_name'), table_name='zipcode2_dataset')
    op.drop_index(op.f('ix_zipcode2_dataset_usps_state_code'), table_name='zipcode2_dataset')
    op.drop_index(op.f('ix_zipcode2_dataset_zip_code'), table_name='zipcode2_dataset')
    op.drop_table('zipcode2_dataset')
