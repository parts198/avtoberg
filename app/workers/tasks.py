import time
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.core.config import get_settings
from app.services.ozon_client import OzonClient
from app import models
from app.services.stock_service import get_or_create_stock
from .celery_app import celery_app

settings = get_settings()
engine = create_engine(
    f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}",
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(bind=engine)


def _rate_limit_sleep():
    time.sleep(60 / settings.OZON_RATE_LIMIT_PER_MINUTE)


@celery_app.task(bind=True, max_retries=5, default_retry_delay=10)
def push_stock(self, store_id: int, stocks: list[dict]):
    db = SessionLocal()
    try:
        store = db.query(models.OzonStore).get(store_id)
        client = OzonClient(store)
        client.update_stocks(db, stocks)
    except Exception as exc:
        raise self.retry(exc=exc)
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=5, default_retry_delay=10)
def push_prices(self, store_id: int, prices: list[dict]):
    db = SessionLocal()
    try:
        store = db.query(models.OzonStore).get(store_id)
        client = OzonClient(store)
        client.update_prices(db, prices)
    except Exception as exc:
        raise self.retry(exc=exc)
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=5, default_retry_delay=30)
def sync_orders(self, store_id: int):
    db = SessionLocal()
    try:
        store = db.query(models.OzonStore).get(store_id)
        client = OzonClient(store)
        response = client._post(db, "/v3/posting/fbo/list", {"limit": 100, "with": {"analytics_data": False, "financial_data": False}})
        for posting in response.get("result", []):
            posting_number = posting.get("posting_number")
            warehouse_id = posting.get("analytics_data", {}).get("warehouse_id") or 0
            status = posting.get("status")
            existing = db.query(models.Order).filter_by(posting_number=posting_number).first()
            if existing:
                existing.status = status
            else:
                order = models.Order(store_id=store.id, posting_number=posting_number, status=status, warehouse_id=warehouse_id)
                db.add(order)
        db.commit()
    except Exception as exc:
        raise self.retry(exc=exc)
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=5, default_retry_delay=10)
def sync_promotions(self, store_id: int):
    db = SessionLocal()
    try:
        store = db.query(models.OzonStore).get(store_id)
        client = OzonClient(store)
        client.list_actions(db)
    except Exception as exc:
        raise self.retry(exc=exc)
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=5, default_retry_delay=10)
def add_products_to_action(self, store_id: int, action_id: str, product_ids: list[int]):
    db = SessionLocal()
    try:
        store = db.query(models.OzonStore).get(store_id)
        client = OzonClient(store)
        client.add_to_action(db, action_id, product_ids)
    except Exception as exc:
        raise self.retry(exc=exc)
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=5, default_retry_delay=10)
def remove_products_from_action(self, store_id: int, action_id: str, product_ids: list[int]):
    db = SessionLocal()
    try:
        store = db.query(models.OzonStore).get(store_id)
        client = OzonClient(store)
        client.remove_from_action(db, action_id, product_ids)
    except Exception as exc:
        raise self.retry(exc=exc)
    finally:
        db.close()
