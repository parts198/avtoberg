from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class ProductGroup(Base):
    __tablename__ = "product_groups"
    id = Column(Integer, primary_key=True, index=True)
    canonical_name = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    items = relationship("ProductGroupItem", back_populates="group", cascade="all, delete-orphan")
    stocks = relationship("Stock", back_populates="product_group", cascade="all, delete-orphan")
    order_items = relationship("OrderItem", back_populates="product_group")


class ProductGroupItem(Base):
    __tablename__ = "product_group_items"
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), primary_key=True)
    product_group_id = Column(Integer, ForeignKey("product_groups.id", ondelete="CASCADE"), primary_key=True)
    confirmed = Column(Boolean, default=False, nullable=False)

    product = relationship("Product", back_populates="group_items")
    group = relationship("ProductGroup", back_populates="items")

    __table_args__ = (
        UniqueConstraint("product_id", "product_group_id", name="uq_product_group_item"),
    )
