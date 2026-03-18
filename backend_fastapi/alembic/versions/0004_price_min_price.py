"""add min_price to prices

Revision ID: 0004_price_min_price
Revises: 0003_price_cost_price
Create Date: 2026-03-18
"""

from alembic import op
import sqlalchemy as sa


revision = '0004_price_min_price'
down_revision = '0003_price_cost_price'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('prices', sa.Column('min_price', sa.Float(), nullable=False, server_default='0'))
    op.execute('UPDATE prices SET min_price = current_price WHERE min_price IS NULL OR min_price <= 0')


def downgrade() -> None:
    op.drop_column('prices', 'min_price')
