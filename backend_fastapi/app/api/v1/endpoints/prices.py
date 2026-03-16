from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.entities import MarketplaceStore, Price, Product, User
from app.schemas.price import PriceListOut, PriceRowOut, PricesApplyMarkupIn, PricesBulkUpdateIn

router = APIRouter(prefix='/prices', tags=['prices'])

ACQUIRING_RATE = 0.019
PACKAGING_COST = 40.0
PROMOTION_RATE = 0.01
DEFAULT_COMMISSION_PERCENT = 12.0
DEFAULT_CUSTOMER_DELIVERY = 30.0
DEFAULT_LOGISTICS = 55.0
DEFAULT_FIRST_MILE = 12.0
DEFAULT_FBS_COST = 15.0


def build_price_row(product: Product, price: Price) -> PriceRowOut:
    current_price = float(price.current_price)
    cost_price = float(price.previous_price) if price.previous_price else round(current_price * 0.7, 2)

    acquiring = round(current_price * ACQUIRING_RATE, 2)
    promotion = round(current_price * PROMOTION_RATE, 2)
    ozon_commission_rub = round(current_price * DEFAULT_COMMISSION_PERCENT / 100, 2)
    payout_to_seller = round(
        current_price
        - acquiring
        - DEFAULT_CUSTOMER_DELIVERY
        - DEFAULT_LOGISTICS
        - DEFAULT_FIRST_MILE
        - PACKAGING_COST
        - promotion
        - ozon_commission_rub
        - DEFAULT_FBS_COST,
        2,
    )
    margin_rub = round(payout_to_seller - cost_price, 2)
    margin_percent = round((margin_rub / current_price) * 100, 2) if current_price else 0.0
    markup_percent = round(((current_price - cost_price) / cost_price) * 100, 2) if cost_price else 0.0

    return PriceRowOut(
        product_id=product.id,
        offer_id=product.article or product.sku,
        title=product.title,
        stock=0,
        fbs=0,
        fbo=0,
        current_price=current_price,
        previous_price=price.previous_price,
        acquiring=acquiring,
        customer_delivery=DEFAULT_CUSTOMER_DELIVERY,
        logistics=DEFAULT_LOGISTICS,
        first_mile=DEFAULT_FIRST_MILE,
        packaging=PACKAGING_COST,
        promotion=promotion,
        ozon_commission_percent=DEFAULT_COMMISSION_PERCENT,
        ozon_commission_rub=ozon_commission_rub,
        cost_price=cost_price,
        fbs_cost=DEFAULT_FBS_COST,
        payout_to_seller=payout_to_seller,
        markup_percent=markup_percent,
        margin_rub=margin_rub,
        margin_percent=margin_percent,
    )


@router.get('', response_model=PriceListOut)
def list_prices(
    store_ids: list[int] | None = Query(default=None),
    search: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=100, ge=1, le=5000),
    sort_by: str = Query(default='stock'),
    sort_order: str = Query(default='desc'),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    owned_store_ids = db.scalars(
        select(MarketplaceStore.id).where(
            MarketplaceStore.user_id == current_user.id,
            MarketplaceStore.is_enabled.is_(True),
        )
    ).all()

    if not owned_store_ids:
        return PriceListOut(total=0, page=page, page_size=page_size, items=[])

    q = (
        select(Product, Price)
        .join(Price, Price.product_id == Product.id)
        .where(Product.store_id.in_(owned_store_ids))
    )

    if store_ids:
        q = q.where(Product.store_id.in_(store_ids))

    if search:
        needle = f'%{search.strip()}%'
        q = q.where((Product.sku.ilike(needle)) | (Product.article.ilike(needle)) | (Product.title.ilike(needle)))

    total = db.scalar(select(func.count()).select_from(q.subquery())) or 0

    sort_column_map = {
        'offer_id': Product.article,
        'price': Price.current_price,
    }
    sort_column = sort_column_map.get(sort_by, Price.current_price)
    q = q.order_by(sort_column.asc() if sort_order == 'asc' else sort_column.desc())

    rows = db.execute(q.offset((page - 1) * page_size).limit(page_size)).all()
    items = [build_price_row(product, price) for product, price in rows]
    return PriceListOut(total=total, page=page, page_size=page_size, items=items)


@router.post('/bulk-update', response_model=PriceListOut)
def bulk_update_prices(
    payload: PricesBulkUpdateIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    product_ids = [x.product_id for x in payload.updates]
    owned_product_ids = set(
        db.scalars(
            select(Product.id)
            .join(MarketplaceStore, MarketplaceStore.id == Product.store_id)
            .where(
                Product.id.in_(product_ids),
                MarketplaceStore.user_id == current_user.id,
                MarketplaceStore.is_enabled.is_(True),
            )
        ).all()
    )

    updates_by_product = {x.product_id: x.new_price for x in payload.updates}
    prices = db.scalars(select(Price).where(Price.product_id.in_(owned_product_ids))).all()
    for row in prices:
        row.previous_price = row.current_price
        row.current_price = updates_by_product[row.product_id]
        row.updated_at = datetime.utcnow()

    db.commit()

    refreshed = db.execute(select(Product, Price).join(Price, Price.product_id == Product.id).where(Product.id.in_(owned_product_ids))).all()
    items = [build_price_row(product, price) for product, price in refreshed]
    return PriceListOut(total=len(items), page=1, page_size=len(items), items=items)


@router.post('/apply-markup', response_model=PriceListOut)
def apply_markup(
    payload: PricesApplyMarkupIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if payload.markup_percent < payload.min_price_markup_percent:
        raise HTTPException(status_code=400, detail='markup_percent must be >= min_price_markup_percent')

    owned_store_ids = db.scalars(
        select(MarketplaceStore.id).where(
            MarketplaceStore.user_id == current_user.id,
            MarketplaceStore.is_enabled.is_(True),
        )
    ).all()

    q = select(Product, Price).join(Price, Price.product_id == Product.id).where(Product.store_id.in_(owned_store_ids))
    if payload.product_ids:
        q = q.where(Product.id.in_(payload.product_ids))

    rows = db.execute(q).all()
    for _product, price in rows:
        base_cost = float(price.previous_price) if price.previous_price else float(price.current_price) * 0.7
        target_markup = max(payload.markup_percent, payload.min_price_markup_percent)
        new_price = round(base_cost * (1 + target_markup / 100), 2)
        if new_price <= 0:
            continue
        price.previous_price = price.current_price
        price.current_price = new_price
        price.updated_at = datetime.utcnow()

    db.commit()

    refreshed = db.execute(q).all()
    items = [build_price_row(product, price) for product, price in refreshed]
    return PriceListOut(total=len(items), page=1, page_size=len(items), items=items)
