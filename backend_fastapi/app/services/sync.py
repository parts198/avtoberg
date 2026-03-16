from datetime import datetime, timezone

from redis import Redis
from rq import Queue
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import decrypt_secret
from app.models.entities import ApiCredential, MarketplaceStore, Order
from app.services.marketplaces import get_marketplace_client


def enqueue_initial_sync(store_id: int) -> str:
    redis_conn = Redis.from_url(settings.redis_url)
    queue = Queue('sync', connection=redis_conn)
    job = queue.enqueue('app.workers.sync_worker.run_initial_sync', store_id)
    return job.id


def get_store_credentials(db: Session, store_id: int) -> dict[str, str]:
    rows = db.scalars(select(ApiCredential).where(ApiCredential.store_id == store_id)).all()
    return {row.key_name: decrypt_secret(row.encrypted_value) for row in rows}


def sync_store_orders(db: Session, store: MarketplaceStore) -> int:
    credentials = get_store_credentials(db, store.id)
    client = get_marketplace_client(store.marketplace)
    raw_orders = client.fetch_orders(credentials)

    synced = 0
    for raw in raw_orders:
        if store.marketplace.value == 'ozon':
            external_id = raw.get('posting_number') or raw.get('order_id') or 'unknown'
            status = raw.get('status', 'unknown')
            date_str = raw.get('in_process_at') or raw.get('created_at')
        else:
            external_id = str(raw.get('srid') or raw.get('odid') or raw.get('gNumber') or 'unknown')
            status = raw.get('cancel_dt') and 'cancelled' or 'new'
            date_str = raw.get('date')

        exists = db.scalar(
            select(Order).where(Order.store_id == store.id, Order.external_order_id == external_id)
        )
        if exists:
            continue

        order_date = (
            datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            if date_str
            else datetime.now(timezone.utc)
        )
        db.add(
            Order(
                store_id=store.id,
                external_order_id=external_id,
                status=status,
                order_date=order_date,
                payload=raw,
            )
        )
        synced += 1

    db.commit()
    return synced
