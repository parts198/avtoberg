"""initial

Revision ID: 0001_initial
Revises: 
Create Date: 2026-03-15
"""

from alembic import op
import sqlalchemy as sa


revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    marketplace = sa.Enum('ozon', 'wildberries', name='marketplace')
    sync_status = sa.Enum('pending', 'running', 'success', 'failed', name='syncstatus')

    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('email', sa.String(length=320), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_users_email', 'users', ['email'])

    op.create_table(
        'marketplace_stores',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('marketplace', marketplace, nullable=False),
        sa.Column('is_enabled', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('connection_status', sa.String(length=50), nullable=False),
        sa.Column('last_sync_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_marketplace_stores_user_id', 'marketplace_stores', ['user_id'])

    op.create_table(
        'api_credentials',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('store_id', sa.Integer(), sa.ForeignKey('marketplace_stores.id'), nullable=False),
        sa.Column('key_name', sa.String(length=100), nullable=False),
        sa.Column('encrypted_value', sa.Text(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_api_credentials_store_id', 'api_credentials', ['store_id'])

    op.create_table(
        'products',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('store_id', sa.Integer(), sa.ForeignKey('marketplace_stores.id'), nullable=False),
        sa.Column('sku', sa.String(length=128), nullable=False),
        sa.Column('article', sa.String(length=128), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False),
    )
    op.create_index('ix_products_store_id', 'products', ['store_id'])
    op.create_index('ix_products_sku', 'products', ['sku'])

    op.create_table(
        'orders',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('store_id', sa.Integer(), sa.ForeignKey('marketplace_stores.id'), nullable=False),
        sa.Column('external_order_id', sa.String(length=128), nullable=False),
        sa.Column('status', sa.String(length=64), nullable=False),
        sa.Column('order_date', sa.DateTime(), nullable=False),
        sa.Column('payload', sa.JSON(), nullable=False),
    )
    op.create_index('ix_orders_store_id', 'orders', ['store_id'])
    op.create_index('ix_orders_external_order_id', 'orders', ['external_order_id'])
    op.create_index('ix_orders_status', 'orders', ['status'])
    op.create_index('ix_orders_order_date', 'orders', ['order_date'])

    op.create_table(
        'supplies',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('store_id', sa.Integer(), sa.ForeignKey('marketplace_stores.id'), nullable=False),
        sa.Column('external_supply_id', sa.String(length=128), nullable=False),
        sa.Column('status', sa.String(length=64), nullable=False),
        sa.Column('planned_date', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_supplies_store_id', 'supplies', ['store_id'])
    op.create_index('ix_supplies_external_supply_id', 'supplies', ['external_supply_id'])

    op.create_table(
        'clusters',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('marketplace', marketplace, nullable=False),
        sa.Column('code', sa.String(length=64), nullable=False, unique=True),
        sa.Column('title', sa.String(length=255), nullable=False),
    )

    op.create_table(
        'prices',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('product_id', sa.Integer(), sa.ForeignKey('products.id'), nullable=False),
        sa.Column('current_price', sa.Float(), nullable=False),
        sa.Column('previous_price', sa.Float(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_prices_product_id', 'prices', ['product_id'])

    op.create_table(
        'stock_snapshots',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('store_id', sa.Integer(), sa.ForeignKey('marketplace_stores.id'), nullable=False),
        sa.Column('product_id', sa.Integer(), sa.ForeignKey('products.id'), nullable=False),
        sa.Column('marketplace_stock', sa.Integer(), nullable=False),
        sa.Column('in_transit_to_customer', sa.Integer(), nullable=False),
        sa.Column('snapshot_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_stock_snapshots_store_id', 'stock_snapshots', ['store_id'])
    op.create_index('ix_stock_snapshots_product_id', 'stock_snapshots', ['product_id'])

    op.create_table(
        'return_items',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('store_id', sa.Integer(), sa.ForeignKey('marketplace_stores.id'), nullable=False),
        sa.Column('product_id', sa.Integer(), sa.ForeignKey('products.id'), nullable=False),
        sa.Column('status', sa.String(length=64), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('payload', sa.JSON(), nullable=False),
    )
    op.create_index('ix_return_items_store_id', 'return_items', ['store_id'])
    op.create_index('ix_return_items_product_id', 'return_items', ['product_id'])
    op.create_index('ix_return_items_status', 'return_items', ['status'])

    op.create_table(
        'sync_jobs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('store_id', sa.Integer(), sa.ForeignKey('marketplace_stores.id'), nullable=False),
        sa.Column('job_type', sa.String(length=64), nullable=False),
        sa.Column('status', sync_status, nullable=False),
        sa.Column('details', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('finished_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_sync_jobs_store_id', 'sync_jobs', ['store_id'])
    op.create_index('ix_sync_jobs_job_type', 'sync_jobs', ['job_type'])

    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('action', sa.String(length=120), nullable=False),
        sa.Column('entity_type', sa.String(length=64), nullable=False),
        sa.Column('entity_id', sa.String(length=64), nullable=False),
        sa.Column('details', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_audit_logs_action', 'audit_logs', ['action'])
    op.create_index('ix_audit_logs_entity_type', 'audit_logs', ['entity_type'])


def downgrade() -> None:
    op.drop_index('ix_audit_logs_entity_type', table_name='audit_logs')
    op.drop_index('ix_audit_logs_action', table_name='audit_logs')
    op.drop_table('audit_logs')
    op.drop_index('ix_sync_jobs_job_type', table_name='sync_jobs')
    op.drop_index('ix_sync_jobs_store_id', table_name='sync_jobs')
    op.drop_table('sync_jobs')
    op.drop_index('ix_return_items_status', table_name='return_items')
    op.drop_index('ix_return_items_product_id', table_name='return_items')
    op.drop_index('ix_return_items_store_id', table_name='return_items')
    op.drop_table('return_items')
    op.drop_index('ix_stock_snapshots_product_id', table_name='stock_snapshots')
    op.drop_index('ix_stock_snapshots_store_id', table_name='stock_snapshots')
    op.drop_table('stock_snapshots')
    op.drop_index('ix_prices_product_id', table_name='prices')
    op.drop_table('prices')
    op.drop_table('clusters')
    op.drop_index('ix_supplies_external_supply_id', table_name='supplies')
    op.drop_index('ix_supplies_store_id', table_name='supplies')
    op.drop_table('supplies')
    op.drop_index('ix_orders_order_date', table_name='orders')
    op.drop_index('ix_orders_status', table_name='orders')
    op.drop_index('ix_orders_external_order_id', table_name='orders')
    op.drop_index('ix_orders_store_id', table_name='orders')
    op.drop_table('orders')
    op.drop_index('ix_products_sku', table_name='products')
    op.drop_index('ix_products_store_id', table_name='products')
    op.drop_table('products')
    op.drop_index('ix_api_credentials_store_id', table_name='api_credentials')
    op.drop_table('api_credentials')
    op.drop_index('ix_marketplace_stores_user_id', table_name='marketplace_stores')
    op.drop_table('marketplace_stores')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')

    sa.Enum(name='syncstatus').drop(op.get_bind(), checkfirst=False)
    sa.Enum(name='marketplace').drop(op.get_bind(), checkfirst=False)
