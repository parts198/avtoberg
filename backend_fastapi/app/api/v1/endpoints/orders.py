from datetime import date, datetime, time

from fastapi import APIRouter, Depends, Query
from sqlalchemy import Text, cast, or_, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.entities import MarketplaceStore, Order, User
from app.schemas.order import OrderDashboardOut, OrderOut

router = APIRouter(prefix='/orders', tags=['orders'])


def _to_float(value: object, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _to_int(value: object, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def _extract_items_from_payload(payload: dict) -> list[dict]:
    if not isinstance(payload, dict):
        return []

    if isinstance(payload.get('products'), list):
        return payload['products']

    if isinstance(payload.get('items'), list):
        return payload['items']

    result = payload.get('result')
    if isinstance(result, dict) and isinstance(result.get('items'), list):
        return result['items']

    return []


def _build_item(raw_item: dict) -> dict:
    offer_id = str(
        raw_item.get('offer_id')
        or raw_item.get('sku')
        or raw_item.get('nmId')
        or ''
    )
    product_name = str(
        raw_item.get('name')
        or raw_item.get('product_name')
        or raw_item.get('subject')
        or ''
    )
    qty = _to_int(raw_item.get('quantity') or raw_item.get('qty') or raw_item.get('count') or 1, 1)
    price = _to_float(raw_item.get('price') or raw_item.get('price_with_disc') or raw_item.get('finished_price') or 0)
    revenue = _to_float(raw_item.get('revenue') or qty * price)
    expenses = _to_float(raw_item.get('expenses_allocated') or raw_item.get('commission_percent') or 0)

    markup = raw_item.get('markup_ratio_fact')
    markup_ratio_fact = _to_float(markup) if markup is not None else None

    product_id_raw = raw_item.get('product_id') or raw_item.get('productId') or raw_item.get('nmId')
    product_id = _to_int(product_id_raw) if product_id_raw is not None else None

    return {
        'product_id': product_id,
        'offer_id': offer_id,
        'product_name': product_name,
        'qty': qty,
        'price': price,
        'revenue': revenue,
        'expenses_allocated': expenses,
        'markup_ratio_fact': markup_ratio_fact,
    }


def _extract_schema(order: Order) -> str:
    payload = order.payload if isinstance(order.payload, dict) else {}
    method = str(
        payload.get('delivery_method')
        or payload.get('fulfillment_type')
        or payload.get('supply_type')
        or ''
    ).upper()

    if method in {'FBO', 'FBS'}:
        return method

    if '/fbo/' in order.external_order_id.lower():
        return 'FBO'

    return 'FBS'


@router.get('/dashboard', response_model=OrderDashboardOut)
def orders_dashboard(
    store_id: int | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    schema: str = Query(default='ALL'),
    offer_id: str = Query(default=''),
    search: str = Query(default=''),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    stores = db.scalars(
        select(MarketplaceStore)
        .where(MarketplaceStore.user_id == current_user.id, MarketplaceStore.is_enabled.is_(True))
        .order_by(MarketplaceStore.name.asc())
    ).all()

    store_map = {store.id: store.name for store in stores}
    owned_store_ids = list(store_map.keys())

    if not owned_store_ids:
        return {
            'stores': [],
            'filters': {
                'store_id': '',
                'date_from': date_from.isoformat() if date_from else '',
                'date_to': date_to.isoformat() if date_to else '',
                'schema': schema.upper() if schema else 'ALL',
                'offer_id': offer_id,
                'search': search,
            },
            'summary': {
                'total_orders': 0,
                'total_items': 0,
                'total_units': 0,
                'total_revenue': 0,
                'total_expenses': 0,
                'status_breakdown': [],
                'scope': 'all_items_in_filtered_orders',
                'scope_label': 'Итоги посчитаны по всем позициям в отфильтрованных заказах.',
            },
            'hourly': [0] * 24,
            'orders': [],
        }

    q = select(Order).where(Order.store_id.in_(owned_store_ids))

    if store_id and store_id in owned_store_ids:
        q = q.where(Order.store_id == store_id)

    if date_from:
        q = q.where(Order.order_date >= datetime.combine(date_from, time.min))

    if date_to:
        q = q.where(Order.order_date <= datetime.combine(date_to, time.max))

    if search:
        search_value = search.strip()
        q = q.where(
            or_(
                Order.external_order_id.ilike(f'%{search_value}%'),
                cast(Order.payload, Text).ilike(f'%{search_value}%'),
            )
        )

    q = q.order_by(Order.order_date.desc(), Order.id.desc()).limit(500)
    orders = db.scalars(q).all()

    schema_upper = (schema or 'ALL').upper()
    offer_filter = (offer_id or '').strip().lower()

    rows: list[dict] = []
    status_counter: dict[str, int] = {}
    hourly = [0] * 24

    total_items = 0
    total_units = 0
    total_revenue = 0.0
    total_expenses = 0.0

    for order in orders:
        resolved_schema = _extract_schema(order)
        if schema_upper != 'ALL' and resolved_schema != schema_upper:
            continue

        raw_items = _extract_items_from_payload(order.payload)
        items = [_build_item(item) for item in raw_items]

        if offer_filter:
            items = [item for item in items if offer_filter in item['offer_id'].lower()]
            if not items:
                continue

        status_counter[order.status] = status_counter.get(order.status, 0) + 1
        hourly[order.order_date.hour] += 1

        items_count = len(items)
        qty_total = sum(item['qty'] for item in items)
        revenue_total = sum(item['revenue'] for item in items)
        expenses_total = sum(item['expenses_allocated'] for item in items)

        markups = [item['markup_ratio_fact'] for item in items if item['markup_ratio_fact'] is not None]
        markup_avg = sum(markups) / len(markups) if markups else None

        total_items += items_count
        total_units += qty_total
        total_revenue += revenue_total
        total_expenses += expenses_total

        rows.append(
            {
                'id': order.id,
                'posting_number': order.external_order_id,
                'status': order.status,
                'schema': resolved_schema,
                'created_at': order.order_date,
                'store_id': order.store_id,
                'store_name': store_map.get(order.store_id, f'Store #{order.store_id}'),
                'first_offer_id': items[0]['offer_id'] if items else '',
                'items_count': items_count,
                'qty_total': qty_total,
                'revenue_total': revenue_total,
                'expenses_total': expenses_total,
                'markup_ratio_avg': markup_avg,
                'items': items,
            }
        )

    status_breakdown = [
        {'status': status_name, 'count': count}
        for status_name, count in sorted(status_counter.items(), key=lambda x: (-x[1], x[0]))
    ]

    summary_scope = 'matched_items' if offer_filter else 'all_items_in_filtered_orders'

    return {
        'stores': [{'id': store.id, 'name': store.name} for store in stores],
        'filters': {
            'store_id': str(store_id) if store_id else '',
            'date_from': date_from.isoformat() if date_from else '',
            'date_to': date_to.isoformat() if date_to else '',
            'schema': schema_upper,
            'offer_id': offer_id,
            'search': search,
        },
        'summary': {
            'total_orders': len(rows),
            'total_items': total_items,
            'total_units': total_units,
            'total_revenue': total_revenue,
            'total_expenses': total_expenses,
            'status_breakdown': status_breakdown,
            'scope': summary_scope,
            'scope_label': (
                'Итоги посчитаны только по позициям, совпавшим с фильтром offer_id.'
                if offer_filter
                else 'Итоги посчитаны по всем позициям в отфильтрованных заказах.'
            ),
        },
        'hourly': hourly,
        'orders': rows,
    }


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
