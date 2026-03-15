from datetime import datetime

from pydantic import BaseModel

from app.models.entities import Marketplace


class StoreCreateIn(BaseModel):
    name: str
    marketplace: Marketplace
    credentials: dict[str, str]


class StoreUpdateIn(BaseModel):
    name: str | None = None
    is_enabled: bool | None = None


class StoreOut(BaseModel):
    id: int
    name: str
    marketplace: Marketplace
    is_enabled: bool
    connection_status: str
    last_sync_at: datetime | None

    class Config:
        from_attributes = True
