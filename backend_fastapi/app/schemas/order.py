from datetime import datetime

from pydantic import BaseModel


class OrderOut(BaseModel):
    id: int
    store_id: int
    external_order_id: str
    status: str
    order_date: datetime
    payload: dict

    class Config:
        from_attributes = True
