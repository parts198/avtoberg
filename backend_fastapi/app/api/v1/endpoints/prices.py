from datetime import datetime
from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from openpyxl import Workbook
from sqlalchemy import func, literal_column, or_, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.entities import AuditLog, Marketplace, MarketplaceStore, Price, Product, StockSnapshot, User
from app.schemas.price import (
    PriceListOut,
    PriceLogEntryOut,
    PricePatchIn,
    PriceRowOut,
    PricesApplyMarkupIn,
    PricesBulkUpdateIn,
    PricesReloadIn,
    PricesReloadOut,
)

router = APIRouter(prefix='/prices', tags=['prices'])

ACQUIRING_RATE = 0.019
PACKAGING_COST = 40.0
PROMOTION_RATE = 0.01
DEFAULT_COMMISSION_PERCENT = 12.0
DEFAULT_CUSTOMER_DELIVERY = 30.0
DEFAULT_LOGISTICS = 55.0
DEFAULT_FIRST_MILE = 12.0
DEFAULT_FBS_COST = 15.0


def _build_price_row(product: Product, price: Price, stock: int = 0) -> PriceRowOut:
    current_price = float(price.current_price)
    cost_price = float(price.previous_price) if price.previous_price else round(current_price * 0.7, 2)

    acquiring = round(current_price * ACQUIRING_RATE, 2)
    promotion = round(current_price * PROMOTION_RATE, 2)
    ozon_commission_rub = round(current_price * DEFAULT_COMMISSION_PERCENT / 100, 2)
    fbs_cost = round(DEFAULT_FBS_COST, 2)
    payout_to_seller = round(
        current_price
        - acquiring
        - DEFAULT_CUSTOMER_DELIVERY
        - DEFAULT_LOGISTICS
        - DEFAULT_FIRST_MILE
        - PACKAGING_COST
        - promotion
        - ozon_commission_rub
        - fbs_cost,
        2,
    )
    margin_rub = round(payout_to_seller - cost_price, 2)
    margin_percent = round((margin_rub / current_price) * 100, 2) if current_price else 0.0
    markup_percent = round(((current_price - cost_price) / cost_price) * 100, 2) if cost_price else 0.0

    return PriceRowOut(
        product_id=product.id,
        offer_id=product.article or product.sku,
        title=product.title,
        stock=stock,
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
        fbs_cost=fbs_cost,
        payout_to_seller=payout_to_seller,
        markup_percent=markup_percent,
        margin_rub=margin_rub,
        margin_percent=margin_percent,
    )


def _get_owned_ozon_store_ids(db: Session, user_id: int) -> list[int]:
    return db.scalars(
        select(MarketplaceStore.id).where(
            MarketplaceStore.user_id == user_id,
            MarketplaceStore.is_enabled.is_(True),
            MarketplaceStore.marketplace == Marketplace.ozon,
        )
    ).all()


def _log_price_action(db: Session, user_id: int, action: str, details: dict):
    db.add(
        AuditLog(
            user_id=user_id,
            action=action,
            entity_type='prices',
            entity_id=str(details.get('store_id', 'global')),
            details=details,
        )
    )


def _fetch_logs(db: Session, user_id: int, limit: int = 20) -> list[PriceLogEntryOut]:
    logs = db.scalars(
        select(AuditLog)
        .where(AuditLog.user_id == user_id, AuditLog.entity_type == 'prices')
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
    ).all()
    return [
        PriceLogEntryOut(
            id=log.id,
            message=f"{log.action}: {log.details}",
            created_at=log.created_at.isoformat(),
        )
        for log in logs
    ]


def _prices_query(db: Session, store_id: int, search: str | None):
    stock_subquery = (
        select(StockSnapshot.product_id, func.sum(StockSnapshot.marketplace_stock).label('stock'))
        .where(StockSnapshot.store_id == store_id)
        .group_by(StockSnapshot.product_id)
        .subquery()
    )

    q = (
        select(Product, Price, func.coalesce(stock_subquery.c.stock, 0).label('stock'))
        .join(Price, Price.product_id == Product.id)
        .outerjoin(stock_subquery, stock_subquery.c.product_id == Product.id)
        .where(Product.store_id == store_id)
    )

    if search:
        needle = f'%{search.strip()}%'
        q = q.where(or_(Product.sku.ilike(needle), Product.article.ilike(needle), Product.title.ilike(needle)))

    return q


@router.get('', response_model=PriceListOut)
def list_prices(
    store_id: int = Query(...),
    search: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=100, ge=1, le=5000),
    sort_by: str = Query(default='stock'),
    sort_order: str = Query(default='desc'),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    owned_store_ids = _get_owned_ozon_store_ids(db, current_user.id)
    if store_id not in owned_store_ids:
        raise HTTPException(status_code=404, detail='Store not found')

    q = _prices_query(db, store_id, search)
    total = db.scalar(select(func.count()).select_from(q.subquery())) or 0

    sort_column_map = {
        'offer_id': Product.article,
        'price': Price.current_price,
        'stock': None,
    }
    sort_column = sort_column_map.get(sort_by)
    if sort_by == 'stock':
        stock_col = literal_column('stock')
        q = q.order_by(stock_col.asc() if sort_order == 'asc' else stock_col.desc())
    elif sort_column is not None:
        q = q.order_by(sort_column.asc() if sort_order == 'asc' else sort_column.desc())

    rows = db.execute(q.offset((page - 1) * page_size).limit(page_size)).all()
    items = [_build_price_row(product, price, stock) for product, price, stock in rows]

    logs = _fetch_logs(db, current_user.id)
    return PriceListOut(total=total, page=page, page_size=page_size, items=items, logs=logs)


@router.post('/reload', response_model=PricesReloadOut)
def reload_prices(
    payload: PricesReloadIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    owned_store_ids = _get_owned_ozon_store_ids(db, current_user.id)
    if payload.store_id not in owned_store_ids:
        raise HTTPException(status_code=404, detail='Store not found')

    now = datetime.utcnow()
    prices = db.scalars(
        select(Price)
        .join(Product, Product.id == Price.product_id)
        .where(Product.store_id == payload.store_id)
    ).all()
    for price in prices:
        price.updated_at = now

    _log_price_action(
        db,
        current_user.id,
        'reload',
        {'store_id': payload.store_id, 'items': len(prices), 'at': now.isoformat()},
    )
    db.commit()
    return PricesReloadOut(status='ok', message=f'Обновлено записей: {len(prices)}')


@router.patch('/{offer_id}', response_model=PriceRowOut)
def update_price(
    offer_id: str,
    payload: PricePatchIn,
    store_id: int = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    owned_store_ids = _get_owned_ozon_store_ids(db, current_user.id)
    if store_id not in owned_store_ids:
        raise HTTPException(status_code=404, detail='Store not found')

    row = db.execute(
        select(Product, Price)
        .join(Price, Price.product_id == Product.id)
        .where(
            Product.store_id == store_id,
            or_(Product.article == offer_id, Product.sku == offer_id),
        )
    ).first()
    if not row:
        raise HTTPException(status_code=404, detail='Offer not found')

    product, price = row
    price.previous_price = price.current_price
    price.current_price = payload.new_price
    price.updated_at = datetime.utcnow()

    _log_price_action(
        db,
        current_user.id,
        'patch',
        {'store_id': store_id, 'offer_id': offer_id, 'new_price': payload.new_price},
    )

    db.commit()
    db.refresh(price)
    return _build_price_row(product, price)


@router.post('/bulk-update', response_model=PriceListOut)
def bulk_update_prices(
    payload: PricesBulkUpdateIn,
    store_id: int = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    owned_store_ids = _get_owned_ozon_store_ids(db, current_user.id)
    if store_id not in owned_store_ids:
        raise HTTPException(status_code=404, detail='Store not found')

    if not payload.updates:
        return PriceListOut(total=0, page=1, page_size=0, items=[], logs=_fetch_logs(db, current_user.id))

    updates_by_offer = {u.offer_id: u.new_price for u in payload.updates}
    rows = db.execute(
        select(Product, Price)
        .join(Price, Price.product_id == Product.id)
        .where(
            Product.store_id == store_id,
            or_(Product.article.in_(list(updates_by_offer.keys())), Product.sku.in_(list(updates_by_offer.keys()))),
        )
    ).all()

    updated_items: list[PriceRowOut] = []
    for product, price in rows:
        offer = product.article or product.sku
        next_price = updates_by_offer.get(offer)
        if next_price is None:
            continue
        price.previous_price = price.current_price
        price.current_price = next_price
        price.updated_at = datetime.utcnow()
        updated_items.append(_build_price_row(product, price))

    _log_price_action(
        db,
        current_user.id,
        'bulk_update',
        {'store_id': store_id, 'items': len(updated_items)},
    )

    db.commit()
    return PriceListOut(total=len(updated_items), page=1, page_size=len(updated_items), items=updated_items, logs=_fetch_logs(db, current_user.id))


@router.get('/export-xlsx')
def export_prices_xlsx(
    store_id: int = Query(...),
    search: str | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    owned_store_ids = _get_owned_ozon_store_ids(db, current_user.id)
    if store_id not in owned_store_ids:
        raise HTTPException(status_code=404, detail='Store not found')

    rows = db.execute(_prices_query(db, store_id, search)).all()

    wb = Workbook()
    ws = wb.active
    ws.title = 'prices'
    ws.append([
        'Артикул',
        'FBS',
        'FBO',
        'Остаток',
        'Цена',
        'Эквайринг',
        'Доставка',
        'Логистика',
        'Первая миля',
        'Упаковка',
        'Продвижение',
        'Комиссия %',
        'Комиссия руб',
        'Себестоимость',
        'Затраты на FBS',
        'К выплате',
        'Наценка',
        'Маржа',
        'Маржинальность',
    ])

    for product, price, stock in rows:
        r = _build_price_row(product, price, stock)
        ws.append([
            r.offer_id,
            r.fbs,
            r.fbo,
            r.stock,
            r.current_price,
            r.acquiring,
            r.customer_delivery,
            r.logistics,
            r.first_mile,
            r.packaging,
            r.promotion,
            r.ozon_commission_percent,
            r.ozon_commission_rub,
            r.cost_price,
            r.fbs_cost,
            r.payout_to_seller,
            r.markup_percent,
            r.margin_rub,
            r.margin_percent,
        ])

    output = BytesIO()
    wb.save(output)
    output.seek(0)

    _log_price_action(db, current_user.id, 'export_xlsx', {'store_id': store_id, 'rows': len(rows)})
    db.commit()

    return StreamingResponse(
        output,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=ozon-prices.xlsx'},
    )


@router.post('/apply-markup', response_model=PriceListOut)
def apply_markup(
    payload: PricesApplyMarkupIn,
    store_id: int = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if payload.markup_percent < payload.min_price_markup_percent:
        raise HTTPException(status_code=400, detail='markup_percent must be >= min_price_markup_percent')

    owned_store_ids = _get_owned_ozon_store_ids(db, current_user.id)
    if store_id not in owned_store_ids:
        raise HTTPException(status_code=404, detail='Store not found')

    q = select(Product, Price).join(Price, Price.product_id == Product.id).where(Product.store_id == store_id)
    if payload.offer_ids:
        q = q.where(or_(Product.article.in_(payload.offer_ids), Product.sku.in_(payload.offer_ids)))

    rows = db.execute(q).all()
    for product, price in rows:
        base_cost = float(price.previous_price) if price.previous_price else float(price.current_price) * 0.7
        target_markup = max(payload.markup_percent, payload.min_price_markup_percent)
        new_price = round(base_cost * (1 + target_markup / 100), 2)
        if new_price <= 0:
            continue
        price.previous_price = price.current_price
        price.current_price = new_price
        price.updated_at = datetime.utcnow()

    _log_price_action(db, current_user.id, 'apply_markup', {'store_id': store_id, 'items': len(rows)})
    db.commit()

    refreshed = db.execute(q).all()
    items = [_build_price_row(product, price) for product, price in refreshed]
    return PriceListOut(total=len(items), page=1, page_size=len(items), items=items, logs=_fetch_logs(db, current_user.id))
