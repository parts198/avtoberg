from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import httpx

from app.models.entities import Marketplace


@dataclass
class ConnectionCheckResult:
    success: bool
    message: str


class MarketplaceClient:
    def check_connection(self, credentials: dict[str, str]) -> ConnectionCheckResult:
        raise NotImplementedError

    def fetch_orders(self, credentials: dict[str, str]) -> list[dict]:
        raise NotImplementedError


class OzonClient(MarketplaceClient):
    base_url = 'https://api-seller.ozon.ru'

    def _headers(self, credentials: dict[str, str]) -> dict[str, str]:
        return {
            'Client-Id': credentials.get('client_id', ''),
            'Api-Key': credentials.get('api_key', ''),
            'Content-Type': 'application/json',
        }

    def check_connection(self, credentials: dict[str, str]) -> ConnectionCheckResult:
        try:
            with httpx.Client(timeout=20) as client:
                response = client.post(
                    f'{self.base_url}/v1/warehouse/list',
                    headers=self._headers(credentials),
                    json={},
                )
            if response.status_code == 200:
                return ConnectionCheckResult(True, 'Подключение к Ozon успешно')
            if response.status_code in (401, 403):
                return ConnectionCheckResult(False, 'Ozon: неверные API ключи')
            return ConnectionCheckResult(False, f'Ozon API error: {response.status_code} {response.text[:200]}')
        except httpx.HTTPError as exc:
            return ConnectionCheckResult(False, f'Ozon connection error: {exc}')

    def fetch_orders(self, credentials: dict[str, str]) -> list[dict]:
        date_from = (datetime.now(timezone.utc) - timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%SZ')
        payload = {
            'dir': 'DESC',
            'filter': {'since': date_from, 'status': ''},
            'limit': 100,
            'offset': 0,
            'with': {'analytics_data': True},
        }
        with httpx.Client(timeout=30) as client:
            response = client.post(
                f'{self.base_url}/v3/posting/fbs/list',
                headers=self._headers(credentials),
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
        return data.get('result', {}).get('postings', [])

    def fetch_all_offer_ids(self, credentials: dict[str, str]) -> list[str]:
        offer_ids: list[str] = []
        limit = 100
        last_id = ''
        guard = 0

        with httpx.Client(timeout=30) as client:
            while guard < 200:
                guard += 1
                response = client.post(
                    f'{self.base_url}/v3/product/list',
                    headers=self._headers(credentials),
                    json={'filter': {'visibility': 'ALL'}, 'last_id': last_id, 'limit': limit},
                )
                response.raise_for_status()
                data = response.json()
                items = data.get('result', {}).get('items', [])

                offer_ids.extend(str(item.get('offer_id') or '').strip() for item in items)
                offer_ids = [offer_id for offer_id in offer_ids if offer_id]

                next_last_id = data.get('result', {}).get('last_id') or ''
                if not next_last_id or next_last_id == last_id or not items:
                    break

                last_id = str(next_last_id)

        # keep order, remove duplicates
        return list(dict.fromkeys(offer_ids))

    def fetch_prices(self, credentials: dict[str, str], offer_ids: list[str]) -> list[dict]:
        if not offer_ids:
            return []

        chunk_size = 100
        items: list[dict] = []

        with httpx.Client(timeout=40) as client:
            for idx in range(0, len(offer_ids), chunk_size):
                chunk = offer_ids[idx : idx + chunk_size]
                response = client.post(
                    f'{self.base_url}/v5/product/info/prices',
                    headers=self._headers(credentials),
                    json={
                        'filter': {'offer_id': chunk, 'visibility': 'ALL'},
                        'limit': len(chunk),
                        'cursor': '',
                    },
                )
                response.raise_for_status()
                payload = response.json()
                if isinstance(payload.get('items'), list):
                    items.extend(payload['items'])

        return items


class WildberriesClient(MarketplaceClient):
    orders_url = 'https://statistics-api.wildberries.ru/api/v1/supplier/orders'
    ping_url = 'https://common-api.wildberries.ru/ping'

    def _headers(self, credentials: dict[str, str]) -> dict[str, str]:
        return {'Authorization': credentials.get('token', '')}

    def check_connection(self, credentials: dict[str, str]) -> ConnectionCheckResult:
        date_from = (datetime.now(timezone.utc) - timedelta(days=1)).strftime('%Y-%m-%d')
        try:
            with httpx.Client(timeout=20) as client:
                response = client.get(
                    self.orders_url,
                    headers=self._headers(credentials),
                    params={'dateFrom': date_from},
                )
            if response.status_code == 200:
                return ConnectionCheckResult(True, 'Подключение к Wildberries успешно')
            if response.status_code in (401, 403):
                return ConnectionCheckResult(False, 'Wildberries: неверный токен API')
            return ConnectionCheckResult(False, f'Wildberries API error: {response.status_code} {response.text[:200]}')
        except httpx.HTTPError as exc:
            return ConnectionCheckResult(False, f'Wildberries connection error: {exc}')

    def fetch_orders(self, credentials: dict[str, str]) -> list[dict]:
        date_from = (datetime.now(timezone.utc) - timedelta(days=7)).strftime('%Y-%m-%d')
        with httpx.Client(timeout=30) as client:
            response = client.get(
                self.orders_url,
                headers=self._headers(credentials),
                params={'dateFrom': date_from},
            )
            response.raise_for_status()
            return response.json()


def get_marketplace_client(marketplace: Marketplace) -> MarketplaceClient:
    if marketplace == Marketplace.ozon:
        return OzonClient()
    return WildberriesClient()
