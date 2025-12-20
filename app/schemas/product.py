from datetime import datetime
from pydantic import BaseModel


class ProductBase(BaseModel):
    product_id: int
    offer_id: str
    sku: int
    name: str


class ProductCreate(ProductBase):
    store_id: int


class ProductOut(ProductBase):
    id: int
    store_id: int
    created_at: datetime

    class Config:
        orm_mode = True


class ProductGroupBase(BaseModel):
    canonical_name: str


class ProductGroupCreate(ProductGroupBase):
    product_ids: list[int]


class ProductGroupOut(ProductGroupBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class ProductGroupItemOut(BaseModel):
    product_id: int
    product_group_id: int
    confirmed: bool

    class Config:
        orm_mode = True
