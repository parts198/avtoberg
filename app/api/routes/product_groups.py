from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import get_current_user
from app.schemas.product import ProductGroupCreate, ProductGroupOut, ProductGroupItemOut
from app import models

router = APIRouter()


@router.post("/", response_model=ProductGroupOut)
def create_group(group_in: ProductGroupCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # ensure all products belong to user's stores and confirmed
    products = db.query(models.Product).filter(models.Product.id.in_(group_in.product_ids)).all()
    store_ids = [s.id for s in db.query(models.OzonStore).filter_by(user_id=current_user.id)]
    for p in products:
        if p.store_id not in store_ids:
            raise HTTPException(status_code=400, detail="Нельзя группировать чужие товары")
    group = models.ProductGroup(canonical_name=group_in.canonical_name)
    db.add(group)
    db.commit()
    db.refresh(group)
    for pid in group_in.product_ids:
        db.add(models.ProductGroupItem(product_id=pid, product_group_id=group.id, confirmed=True))
    db.commit()
    db.refresh(group)
    return group


@router.get("/", response_model=list[ProductGroupOut])
def list_groups(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    store_ids = [s.id for s in db.query(models.OzonStore).filter_by(user_id=current_user.id)]
    product_ids = [p.id for p in db.query(models.Product).filter(models.Product.store_id.in_(store_ids))]
    group_ids = {item.product_group_id for item in db.query(models.ProductGroupItem).filter(models.ProductGroupItem.product_id.in_(product_ids))}
    return db.query(models.ProductGroup).filter(models.ProductGroup.id.in_(group_ids)).all()


@router.post("/{group_id}/confirm/{product_id}", response_model=ProductGroupItemOut)
def confirm_product(group_id: int, product_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    item = db.query(models.ProductGroupItem).filter_by(product_group_id=group_id, product_id=product_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Элемент не найден")
    store_ids = [s.id for s in db.query(models.OzonStore).filter_by(user_id=current_user.id)]
    if item.product.store_id not in store_ids:
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    item.confirmed = True
    db.commit()
    db.refresh(item)
    return item
