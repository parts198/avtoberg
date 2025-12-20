from sqlalchemy import Column, Integer, ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class Stock(Base):
    __tablename__ = "stocks"
    id = Column(Integer, primary_key=True)
    product_group_id = Column(Integer, ForeignKey("product_groups.id", ondelete="CASCADE"), nullable=False)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False)
    available_qty = Column(Integer, nullable=False, default=0)
    reserved_qty = Column(Integer, nullable=False, default=0)

    product_group = relationship("ProductGroup", back_populates="stocks")
    warehouse = relationship("Warehouse", back_populates="stocks")

    __table_args__ = (
        UniqueConstraint("product_group_id", "warehouse_id", name="uq_stock_group_warehouse"),
    )
