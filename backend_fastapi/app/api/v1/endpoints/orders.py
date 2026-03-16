from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import Text, cast, or_, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.entities import MarketplaceStore, Order, User
from app.schemas.order import OrderOut

router = APIRouter(prefix='/orders', tags=['orders'])


@router.get('', response_model=list[OrderOut])
def list_orders(
    store_ids: list[int] | None = Query(default=None),
    status: str | None = Query(default=None),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    search: str | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    owned_store_ids = db.scalars(
        select(MarketplaceStore.id).where(MarketplaceStore.user_id == current_user.id)
    ).all()

    q = select(Order).where(Order.store_id.in_(owned_store_ids))
    if store_ids:
        q = q.where(Order.store_id.in_(store_ids))
    if status:
        q = q.where(Order.status == status)
    if date_from:
        q = q.where(Order.order_date >= date_from)
    if date_to:
        q = q.where(Order.order_date <= date_to)
    if search:
        q = q.where(
            or_(
                Order.external_order_id.ilike(f'%{search}%'),
                cast(Order.payload, Text).ilike(f'%{search}%'),
            )
        )

    q = q.order_by(Order.order_date.desc()).limit(500)
    return db.scalars(q).all()
