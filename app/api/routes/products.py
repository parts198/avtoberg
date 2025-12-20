from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import get_current_user
from app.schemas.product import ProductCreate, ProductOut
from app.services.stock_service import normalize_offer
from app import models

router = APIRouter()


@router.post("/", response_model=ProductOut)
def create_product(product_in: ProductCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    store = db.query(models.OzonStore).filter_by(id=product_in.store_id, user_id=current_user.id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Магазин не найден")
    product = models.Product(**product_in.dict())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.get("/", response_model=list[ProductOut])
def list_products(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    store_ids = [s.id for s in db.query(models.OzonStore).filter_by(user_id=current_user.id).all()]
    return db.query(models.Product).filter(models.Product.store_id.in_(store_ids)).all()


@router.get("/matches/{offer_id}", response_model=list[ProductOut])
def match_offer(offer_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    norm = normalize_offer(offer_id)
    store_ids = [s.id for s in db.query(models.OzonStore).filter_by(user_id=current_user.id).all()]
    matches = db.query(models.Product).filter(models.Product.store_id.in_(store_ids)).all()
    return [p for p in matches if normalize_offer(p.offer_id) == norm]
