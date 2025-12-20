from datetime import datetime
from pydantic import BaseModel


class WarehouseBase(BaseModel):
    store_id: int
    warehouse_id: int
    name: str
    type: str
    active: bool = True


class WarehouseCreate(WarehouseBase):
    pass


class WarehouseOut(WarehouseBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
