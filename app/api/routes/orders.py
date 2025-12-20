from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import get_current_user
from app.schemas.order import OrderCreate, OrderOut
from app.services import stock_service
from app import models

router = APIRouter()


@router.post("/", response_model=OrderOut)
def create_order(order_in: OrderCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    store = db.query(models.OzonStore).filter_by(id=order_in.store_id, user_id=current_user.id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Магазин не найден")
    warehouse = db.query(models.Warehouse).get(order_in.warehouse_id)
    if not warehouse or warehouse.store_id != store.id:
        raise HTTPException(status_code=400, detail="Склад не принадлежит магазину")
    order = models.Order(store_id=store.id, posting_number=order_in.posting_number, status=order_in.status, warehouse_id=order_in.warehouse_id)
    db.add(order)
    db.commit()
    db.refresh(order)
    for item in order_in.items:
        db.add(models.OrderItem(order_id=order.id, product_group_id=item.product_group_id, quantity=item.quantity))
    db.commit()
    db.refresh(order)
    db.refresh(order, attribute_names=["items"])
    _apply_status_logic(order, order_in.status, db)
    db.refresh(order)
    return order


def _apply_status_logic(order: models.Order, status: str, db: Session):
    if status in {"created", "awaiting_registration"}:
        stock_service.reserve(db, order)
    elif status == "awaiting_delivery":
        stock_service.commit_reserve(db, order)
    elif status == "cancelled":
        stock_service.release_reserve(db, order)


@router.get("/", response_model=list[OrderOut])
def list_orders(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    store_ids = [s.id for s in db.query(models.OzonStore).filter_by(user_id=current_user.id)]
    return db.query(models.Order).filter(models.Order.store_id.in_(store_ids)).all()
