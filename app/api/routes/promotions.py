from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import get_current_user
from app.schemas.promotion import PromotionCandidatesRequest, PromotionChangeRequest
from app.services.ozon_client import OzonClient
from app.workers import tasks
from app import models

router = APIRouter()


def _get_store(db: Session, store_id: int, user: models.User) -> models.OzonStore:
    store = db.query(models.OzonStore).filter_by(id=store_id, user_id=user.id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Магазин не найден")
    return store


@router.get("/{store_id}")
def list_promotions(store_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    store = _get_store(db, store_id, current_user)
    client = OzonClient(store)
    return client.list_actions(db)


@router.post("/{store_id}/candidates")
def candidates(store_id: int, payload: PromotionCandidatesRequest, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    store = _get_store(db, store_id, current_user)
    client = OzonClient(store)
    return client.action_candidates(db, payload.action_id, payload.limit, payload.offset)


@router.post("/{store_id}/add")
def add_products(store_id: int, payload: PromotionChangeRequest, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    _get_store(db, store_id, current_user)
    tasks.add_products_to_action.delay(store_id, payload.action_id, payload.product_ids)
    return {"status": "queued"}


@router.post("/{store_id}/remove")
def remove_products(store_id: int, payload: PromotionChangeRequest, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    _get_store(db, store_id, current_user)
    tasks.remove_products_from_action.delay(store_id, payload.action_id, payload.product_ids)
    return {"status": "queued"}
