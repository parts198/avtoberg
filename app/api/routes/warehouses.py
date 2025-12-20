from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import get_current_user
from app.schemas.warehouse import WarehouseCreate, WarehouseOut
from app import models

router = APIRouter()


@router.post("/", response_model=WarehouseOut)
def create_warehouse(warehouse_in: WarehouseCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    store = db.query(models.OzonStore).filter_by(id=warehouse_in.store_id, user_id=current_user.id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Магазин не найден")
    warehouse = models.Warehouse(**warehouse_in.dict())
    db.add(warehouse)
    db.commit()
    db.refresh(warehouse)
    return warehouse


@router.get("/", response_model=list[WarehouseOut])
def list_warehouses(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    store_ids = [s.id for s in db.query(models.OzonStore).filter_by(user_id=current_user.id)]
    return db.query(models.Warehouse).filter(models.Warehouse.store_id.in_(store_ids)).all()
