from sqlalchemy.orm import Session
from fastapi import HTTPException
from app import models


def normalize_offer(offer_id: str) -> str:
    return offer_id.replace("-", "").lower()


def get_or_create_stock(db: Session, product_group_id: int, warehouse_id: int) -> models.Stock:
    stock = (
        db.query(models.Stock)
        .filter_by(product_group_id=product_group_id, warehouse_id=warehouse_id)
        .one_or_none()
    )
    if not stock:
        stock = models.Stock(product_group_id=product_group_id, warehouse_id=warehouse_id, available_qty=0, reserved_qty=0)
        db.add(stock)
        db.commit()
        db.refresh(stock)
    return stock


def reserve(db: Session, order: models.Order):
    for item in order.items:
        stock = get_or_create_stock(db, item.product_group_id, order.warehouse_id)
        if stock.available_qty - stock.reserved_qty < item.quantity:
            raise HTTPException(status_code=400, detail="Недостаточно доступного остатка")
        stock.reserved_qty += item.quantity
        log = models.ReservationLog(order_id=order.id, product_group_id=item.product_group_id, warehouse_id=order.warehouse_id, quantity=item.quantity, action="reserve")
        db.add(log)
        db.add(models.StockLog(product_group_id=item.product_group_id, warehouse_id=order.warehouse_id, delta_available=0, delta_reserved=item.quantity, reason=f"reserve order {order.posting_number}"))
    db.commit()


def release_reserve(db: Session, order: models.Order):
    for item in order.items:
        stock = get_or_create_stock(db, item.product_group_id, order.warehouse_id)
        stock.reserved_qty = max(0, stock.reserved_qty - item.quantity)
        db.add(models.ReservationLog(order_id=order.id, product_group_id=item.product_group_id, warehouse_id=order.warehouse_id, quantity=item.quantity, action="release"))
        db.add(models.StockLog(product_group_id=item.product_group_id, warehouse_id=order.warehouse_id, delta_available=0, delta_reserved=-item.quantity, reason=f"release order {order.posting_number}"))
    db.commit()


def commit_reserve(db: Session, order: models.Order):
    for item in order.items:
        stock = get_or_create_stock(db, item.product_group_id, order.warehouse_id)
        if stock.reserved_qty < item.quantity:
            raise HTTPException(status_code=400, detail="Недостаточный резерв")
        stock.reserved_qty -= item.quantity
        stock.available_qty = max(0, stock.available_qty - item.quantity)
        db.add(models.ReservationLog(order_id=order.id, product_group_id=item.product_group_id, warehouse_id=order.warehouse_id, quantity=item.quantity, action="commit"))
        db.add(models.StockLog(product_group_id=item.product_group_id, warehouse_id=order.warehouse_id, delta_available=-item.quantity, delta_reserved=-item.quantity, reason=f"commit order {order.posting_number}"))
    db.commit()
