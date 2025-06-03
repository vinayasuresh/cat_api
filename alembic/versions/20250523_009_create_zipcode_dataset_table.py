"""create zipcode_dataset table

Revision ID: 20250523009
Revises: 20250523008
Create Date: 2025-05-23 00:09:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision = '20250523009'
down_revision = '20250523008'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'zipcode_dataset',
        sa.Column('zip', sa.String(), nullable=False),
        sa.Column('lat', sa.Float(), nullable=True),
        sa.Column('lng', sa.Float(), nullable=True),
        sa.Column('city', sa.String(), nullable=True),
        sa.Column('state_id', sa.String(), nullable=True),
        sa.Column('state_name', sa.String(), nullable=True),
        sa.Column('zcta', sa.Boolean(), nullable=True),
        sa.Column('parent_zcta', sa.String(), nullable=True),
        sa.Column('population', sa.Float(), nullable=True),
        sa.Column('density', sa.Float(), nullable=True),
        sa.Column('county_fips', sa.String(), nullable=True),
        sa.Column('county_name', sa.String(), nullable=True),
        sa.Column('county_weights', sa.JSON(), nullable=True),
        sa.Column('county_names_all', sa.String(), nullable=True),
        sa.Column('county_fips_all', sa.String(), nullable=True),
        sa.Column('imprecise', sa.Boolean(), nullable=True),
        sa.Column('military', sa.Boolean(), nullable=True),
        sa.Column('timezone', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('zip')
    )
    op.create_index(op.f('ix_zipcode_dataset_zip'), 'zipcode_dataset', ['zip'], unique=False)
    op.create_index(op.f('ix_zipcode_dataset_state_id'), 'zipcode_dataset', ['state_id'], unique=False)
    op.create_index(op.f('ix_zipcode_dataset_state_name'), 'zipcode_dataset', ['state_name'], unique=False)
    op.create_index(op.f('ix_zipcode_dataset_county_fips'), 'zipcode_dataset', ['county_fips'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_zipcode_dataset_county_fips'), table_name='zipcode_dataset')
    op.drop_index(op.f('ix_zipcode_dataset_state_name'), table_name='zipcode_dataset')
    op.drop_index(op.f('ix_zipcode_dataset_state_id'), table_name='zipcode_dataset')
    op.drop_index(op.f('ix_zipcode_dataset_zip'), table_name='zipcode_dataset')
    op.drop_table('zipcode_dataset')
