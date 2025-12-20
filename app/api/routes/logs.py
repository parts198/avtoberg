from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import get_current_user
from app.schemas.log import ApiLogOut
from app import models

router = APIRouter()


@router.get("/api", response_model=list[ApiLogOut])
def api_logs(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    store_ids = [s.id for s in db.query(models.OzonStore).filter_by(user_id=current_user.id)]
    return db.query(models.ApiLog).filter(models.ApiLog.store_id.in_(store_ids)).order_by(models.ApiLog.created_at.desc()).limit(200).all()
