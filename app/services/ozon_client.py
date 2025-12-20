import time
import httpx
from typing import Any, Dict, Optional
from app.core.config import get_settings
from app.models import ApiLog, OzonStore
from sqlalchemy.orm import Session
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

settings = get_settings()


class OzonAPIError(Exception):
    pass


def log_api(db: Session, store: OzonStore, direction: str, endpoint: str, payload: Any, status_code: Optional[int] = None):
    entry = ApiLog(
        store_id=store.id,
        direction=direction,
        endpoint=endpoint,
        status_code=status_code,
        payload=payload,
    )
    db.add(entry)
    db.commit()


class OzonClient:
    def __init__(self, store: OzonStore):
        self.store = store
        self.headers = {
            "Client-Id": store.client_id,
            "Api-Key": store.api_key,
            "Content-Type": "application/json",
        }
        self.client = httpx.Client(base_url=settings.OZON_API_URL, headers=self.headers, timeout=30.0)

    def _handle_response(self, db: Session, endpoint: str, response: httpx.Response) -> Dict[str, Any]:
        log_api(db, self.store, "response", endpoint, response.json(), status_code=response.status_code)
        if response.status_code >= 400:
            raise OzonAPIError(response.text)
        return response.json()

    @retry(stop=stop_after_attempt(settings.BACKOFF_MAX_RETRIES), wait=wait_exponential(multiplier=settings.BACKOFF_BASE), reraise=True)
    def _post(self, db: Session, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        log_api(db, self.store, "request", endpoint, payload)
        response = self.client.post(endpoint, json=payload)
        if response.status_code == 429:
            time.sleep(1)
            raise OzonAPIError("Rate limit exceeded")
        return self._handle_response(db, endpoint, response)

    def get_products(self, db: Session, page_size: int = 100) -> Dict[str, Any]:
        return self._post(db, "/v2/product/list", {"page_size": page_size, "page": 1})

    def get_product_info(self, db: Session, product_id: int) -> Dict[str, Any]:
        return self._post(db, "/v2/product/info", {"product_id": product_id})

    def update_stocks(self, db: Session, stocks: list[dict[str, Any]]):
        return self._post(db, "/v2/products/stocks", {"stocks": stocks})

    def update_prices(self, db: Session, prices: list[dict[str, Any]]):
        return self._post(db, "/v1/product/import/prices", {"prices": prices})

    def list_actions(self, db: Session):
        return self._post(db, "/v1/actions", {})

    def list_action_products(self, db: Session, action_id: str, limit: int = 100, offset: int = 0):
        return self._post(db, "/v1/actions/products", {"action_id": action_id, "limit": limit, "offset": offset})

    def action_candidates(self, db: Session, action_id: str, limit: int = 100, offset: int = 0):
        return self._post(db, "/v1/actions/candidates", {"action_id": action_id, "limit": limit, "offset": offset})

    def add_to_action(self, db: Session, action_id: str, product_ids: list[int]):
        return self._post(db, "/v1/actions/products/add", {"action_id": action_id, "product_ids": product_ids})

    def remove_from_action(self, db: Session, action_id: str, product_ids: list[int]):
        return self._post(db, "/v1/actions/products/remove", {"action_id": action_id, "product_ids": product_ids})
