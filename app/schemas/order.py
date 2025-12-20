from datetime import datetime
from pydantic import BaseModel
from typing import List


class OrderItemBase(BaseModel):
    product_group_id: int
    quantity: int


class OrderCreate(BaseModel):
    store_id: int
    posting_number: str
    status: str
    warehouse_id: int
    items: List[OrderItemBase]


class OrderItemOut(OrderItemBase):
    id: int
    product_id: int | None

    class Config:
        orm_mode = True


class OrderOut(BaseModel):
    id: int
    store_id: int
    posting_number: str
    status: str
    warehouse_id: int
    created_at: datetime
    items: List[OrderItemOut]

    class Config:
        orm_mode = True
