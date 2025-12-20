from datetime import datetime
from pydantic import BaseModel


class StoreBase(BaseModel):
    name: str
    client_id: str
    api_key: str
    active: bool = True


class StoreCreate(StoreBase):
    pass


class StoreUpdate(BaseModel):
    name: str | None = None
    client_id: str | None = None
    api_key: str | None = None
    active: bool | None = None


class StoreOut(StoreBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
