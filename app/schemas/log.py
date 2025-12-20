from datetime import datetime
from pydantic import BaseModel


class ApiLogOut(BaseModel):
    id: int
    store_id: int
    direction: str
    endpoint: str
    status_code: int | None
    payload: dict | None
    created_at: datetime

    class Config:
        orm_mode = True
