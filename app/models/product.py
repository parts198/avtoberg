from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base


class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("ozon_stores.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, nullable=False)  # Ozon product_id
    offer_id = Column(String, index=True, nullable=False)
    sku = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    store = relationship("OzonStore", back_populates="products")
    group_items = relationship("ProductGroupItem", back_populates="product", cascade="all, delete-orphan")
    order_items = relationship("OrderItem", back_populates="product", cascade="all, delete-orphan")
