import logging
from datetime import datetime

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.entities import MarketplaceStore, SyncJob, SyncStatus
from app.services.sync import sync_store_orders

logger = logging.getLogger(__name__)


def run_initial_sync(store_id: int):
    db = SessionLocal()
    try:
        job = db.scalar(
            select(SyncJob).where(SyncJob.store_id == store_id, SyncJob.job_type == 'initial_sync')
        )
        store = db.get(MarketplaceStore, store_id)
        if not job or not store:
            return

        job.status = SyncStatus.running
        job.started_at = datetime.utcnow()
        db.commit()

        synced_orders = sync_store_orders(db, store)

        store.last_sync_at = datetime.utcnow()
        job.status = SyncStatus.success
        job.finished_at = datetime.utcnow()
        details = dict(job.details or {})
        details['synced_orders'] = synced_orders
        job.details = details
        db.commit()
    except Exception as exc:  # noqa: BLE001
        logger.exception('Initial sync failed for store=%s: %s', store_id, exc)
        job = db.scalar(
            select(SyncJob).where(SyncJob.store_id == store_id, SyncJob.job_type == 'initial_sync')
        )
        if job:
            job.status = SyncStatus.failed
            job.finished_at = datetime.utcnow()
            details = dict(job.details or {})
            details['error'] = str(exc)
            job.details = details
            db.commit()
    finally:
        db.close()
