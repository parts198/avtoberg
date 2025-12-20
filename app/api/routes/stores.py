from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.store import StoreCreate, StoreOut, StoreUpdate
from app.core.security import get_current_user
from app import models

router = APIRouter()


@router.post("/", response_model=StoreOut)
def create_store(store_in: StoreCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    store = models.OzonStore(**store_in.dict(), user_id=current_user.id)
    db.add(store)
    db.commit()
    db.refresh(store)
    return store


@router.get("/", response_model=list[StoreOut])
def list_stores(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.OzonStore).filter_by(user_id=current_user.id).all()


@router.put("/{store_id}", response_model=StoreOut)
def update_store(store_id: int, store_in: StoreUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    store = db.query(models.OzonStore).filter_by(id=store_id, user_id=current_user.id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Магазин не найден")
    for field, value in store_in.dict(exclude_unset=True).items():
        setattr(store, field, value)
    db.commit()
    db.refresh(store)
    return store
