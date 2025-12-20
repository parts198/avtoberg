from pydantic import BaseModel
from typing import List


class StockUpdate(BaseModel):
    product_group_id: int
    warehouse_id: int
    available_qty: int


class StockOut(BaseModel):
    product_group_id: int
    warehouse_id: int
    available_qty: int
    reserved_qty: int

    class Config:
        orm_mode = True


class StockFileItem(BaseModel):
    offer_id: str
    warehouse: str
    quantity: int


class StockImportResult(BaseModel):
    updated: int
    skipped: List[str]
