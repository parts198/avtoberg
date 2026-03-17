import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Marketplace(str, enum.Enum):
    ozon = 'ozon'
    wildberries = 'wildberries'


class SyncStatus(str, enum.Enum):
    pending = 'pending'
    running = 'running'
    success = 'success'
    failed = 'failed'


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    stores: Mapped[list['MarketplaceStore']] = relationship(back_populates='user')


class MarketplaceStore(Base):
    __tablename__ = 'marketplace_stores'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    name: Mapped[str] = mapped_column(String(255))
    marketplace: Mapped[Marketplace] = mapped_column(Enum(Marketplace))
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    connection_status: Mapped[str] = mapped_column(String(50), default='new')
    last_sync_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    user: Mapped['User'] = relationship(back_populates='stores')
    credentials: Mapped[list['ApiCredential']] = relationship(back_populates='store')


class ApiCredential(Base):
    __tablename__ = 'api_credentials'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    store_id: Mapped[int] = mapped_column(ForeignKey('marketplace_stores.id'), index=True)
    key_name: Mapped[str] = mapped_column(String(100))
    encrypted_value: Mapped[str] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    store: Mapped['MarketplaceStore'] = relationship(back_populates='credentials')


class Product(Base):
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    store_id: Mapped[int] = mapped_column(ForeignKey('marketplace_stores.id'), index=True)
    sku: Mapped[str] = mapped_column(String(128), index=True)
    article: Mapped[str | None] = mapped_column(String(128), nullable=True)
    title: Mapped[str] = mapped_column(String(255))


class Price(Base):
    __tablename__ = 'prices'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'), index=True)
    current_price: Mapped[float] = mapped_column(Float)
    previous_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    cost_price: Mapped[float] = mapped_column(Float, default=0)
    ozon_data: Mapped[dict] = mapped_column(JSON, default=dict)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Order(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    store_id: Mapped[int] = mapped_column(ForeignKey('marketplace_stores.id'), index=True)
    external_order_id: Mapped[str] = mapped_column(String(128), index=True)
    status: Mapped[str] = mapped_column(String(64), index=True)
    order_date: Mapped[datetime] = mapped_column(DateTime, index=True)
    payload: Mapped[dict] = mapped_column(JSON)


class Supply(Base):
    __tablename__ = 'supplies'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    store_id: Mapped[int] = mapped_column(ForeignKey('marketplace_stores.id'), index=True)
    external_supply_id: Mapped[str] = mapped_column(String(128), index=True)
    status: Mapped[str] = mapped_column(String(64))
    planned_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class Cluster(Base):
    __tablename__ = 'clusters'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    marketplace: Mapped[Marketplace] = mapped_column(Enum(Marketplace))
    code: Mapped[str] = mapped_column(String(64), unique=True)
    title: Mapped[str] = mapped_column(String(255))


class StockSnapshot(Base):
    __tablename__ = 'stock_snapshots'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    store_id: Mapped[int] = mapped_column(ForeignKey('marketplace_stores.id'), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'), index=True)
    marketplace_stock: Mapped[int] = mapped_column(Integer, default=0)
    in_transit_to_customer: Mapped[int] = mapped_column(Integer, default=0)
    snapshot_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ReturnItem(Base):
    __tablename__ = 'return_items'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    store_id: Mapped[int] = mapped_column(ForeignKey('marketplace_stores.id'), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'), index=True)
    status: Mapped[str] = mapped_column(String(64), index=True)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    payload: Mapped[dict] = mapped_column(JSON)


class SyncJob(Base):
    __tablename__ = 'sync_jobs'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    store_id: Mapped[int] = mapped_column(ForeignKey('marketplace_stores.id'), index=True)
    job_type: Mapped[str] = mapped_column(String(64), index=True)
    status: Mapped[SyncStatus] = mapped_column(Enum(SyncStatus), default=SyncStatus.pending)
    details: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class AuditLog(Base):
    __tablename__ = 'audit_logs'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey('users.id'), nullable=True)
    action: Mapped[str] = mapped_column(String(120), index=True)
    entity_type: Mapped[str] = mapped_column(String(64), index=True)
    entity_id: Mapped[str] = mapped_column(String(64))
    details: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
