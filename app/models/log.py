from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class ApiLog(Base):
    __tablename__ = "api_logs"
    id = Column(Integer, primary_key=True)
    store_id = Column(Integer, ForeignKey("ozon_stores.id", ondelete="CASCADE"), nullable=False)
    direction = Column(String, nullable=False)  # request | response
    endpoint = Column(String, nullable=False)
    status_code = Column(Integer, nullable=True)
    payload = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    store = relationship("OzonStore")


class StockLog(Base):
    __tablename__ = "stock_logs"
    id = Column(Integer, primary_key=True)
    product_group_id = Column(Integer, ForeignKey("product_groups.id", ondelete="CASCADE"), nullable=False)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False)
    delta_available = Column(Integer, nullable=False)
    delta_reserved = Column(Integer, nullable=False)
    reason = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    product_group = relationship("ProductGroup")
    warehouse = relationship("Warehouse")


class ReservationLog(Base):
    __tablename__ = "reservation_logs"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_group_id = Column(Integer, ForeignKey("product_groups.id", ondelete="CASCADE"), nullable=False)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, nullable=False)
    action = Column(String, nullable=False)  # reserve | release | commit
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    order = relationship("Order")
    product_group = relationship("ProductGroup")
    warehouse = relationship("Warehouse")
