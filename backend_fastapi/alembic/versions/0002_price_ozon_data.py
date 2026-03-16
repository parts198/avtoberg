"""add ozon_data to prices

Revision ID: 0002_price_ozon_data
Revises: 0001_initial
Create Date: 2026-03-16
"""

from alembic import op
import sqlalchemy as sa


revision = '0002_price_ozon_data'
down_revision = '0001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('prices', sa.Column('ozon_data', sa.JSON(), nullable=False, server_default=sa.text("'{}'")))


def downgrade() -> None:
    op.drop_column('prices', 'ozon_data')
