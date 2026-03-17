"""add cost_price to prices

Revision ID: 0003_price_cost_price
Revises: 0002_price_ozon_data
Create Date: 2026-03-17
"""

from alembic import op
import sqlalchemy as sa


revision = '0003_price_cost_price'
down_revision = '0002_price_ozon_data'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('prices', sa.Column('cost_price', sa.Float(), nullable=False, server_default='0'))


def downgrade() -> None:
    op.drop_column('prices', 'cost_price')
