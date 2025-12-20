import csv
from io import StringIO
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import get_current_user
from app.schemas.stock import StockUpdate, StockOut, StockImportResult
from app.services.stock_service import get_or_create_stock, normalize_offer
from app import models

router = APIRouter()


@router.get("/", response_model=list[StockOut])
def list_stocks(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    store_ids = [s.id for s in db.query(models.OzonStore).filter_by(user_id=current_user.id)]
    warehouse_ids = [w.id for w in db.query(models.Warehouse).filter(models.Warehouse.store_id.in_(store_ids))]
    stocks = db.query(models.Stock).filter(models.Stock.warehouse_id.in_(warehouse_ids)).all()
    return stocks


@router.post("/", response_model=StockOut)
def update_stock(stock_in: StockUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    warehouse = db.query(models.Warehouse).get(stock_in.warehouse_id)
    if not warehouse or warehouse.store.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Склад не найден")
    stock = get_or_create_stock(db, stock_in.product_group_id, stock_in.warehouse_id)
    previous_available = stock.available_qty
    stock.available_qty = stock_in.available_qty
    db.add(models.StockLog(
        product_group_id=stock_in.product_group_id,
        warehouse_id=stock_in.warehouse_id,
        delta_available=stock_in.available_qty - previous_available,
        delta_reserved=0,
        reason="manual update",
    ))
    db.commit()
    db.refresh(stock)
    return stock


@router.post("/import", response_model=StockImportResult)
def import_stock(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    content = file.file.read().decode("utf-8")
    reader = csv.DictReader(StringIO(content))
    updated = 0
    skipped: list[str] = []
    for row in reader:
        offer = row.get("offer_id")
        warehouse_name = row.get("warehouse")
        qty = int(row.get("quantity", 0))
        if not offer or warehouse_name is None:
            skipped.append(str(row))
            continue
        normalized = normalize_offer(offer)
        store_ids = [s.id for s in db.query(models.OzonStore).filter_by(user_id=current_user.id)]
        candidates = db.query(models.Product).filter(models.Product.store_id.in_(store_ids)).all()
        matched = [p for p in candidates if normalize_offer(p.offer_id) == normalized]
        if not matched:
            skipped.append(offer)
            continue
        # require confirmed groups
        group_items = db.query(models.ProductGroupItem).filter(models.ProductGroupItem.product_id.in_([m.id for m in matched]), models.ProductGroupItem.confirmed == True).all()
        if not group_items:
            skipped.append(offer)
            continue
        group_id = group_items[0].product_group_id
        warehouse = db.query(models.Warehouse).filter(models.Warehouse.name == warehouse_name, models.Warehouse.store_id.in_(store_ids)).first()
        if not warehouse:
            skipped.append(warehouse_name)
            continue
        stock = get_or_create_stock(db, group_id, warehouse.id)
        stock.available_qty = qty
        updated += 1
    db.commit()
    return StockImportResult(updated=updated, skipped=skipped)
