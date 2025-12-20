from pydantic import BaseModel
from typing import List


class PromotionOut(BaseModel):
    id: str
    title: str
    type: str


class PromotionCandidatesRequest(BaseModel):
    action_id: str
    limit: int = 100
    offset: int = 0


class PromotionChangeRequest(BaseModel):
    action_id: str
    product_ids: List[int]
