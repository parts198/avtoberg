import time
import json
import requests
from django.conf import settings
from audit.models import ApiRequestLog, ApiErrorLog

class OzonClient:
    def __init__(self, client_id, api_key, store_id=None):
        self.client_id = client_id
        self.api_key = api_key
        self.store_id = store_id

    def post(self, path, payload):
        url = settings.OZON_API_URL + path
        headers = {
            'Client-Id': self.client_id,
            'Api-Key': self.api_key,
            'Content-Type': 'application/json'
        }
        start = time.time()
        try:
            resp = requests.post(url, headers=headers, data=json.dumps(payload))
            duration = int((time.time() - start) * 1000)
            ApiRequestLog.objects.create(method='POST', url=path, request_body=json.dumps(payload), response_body=resp.text, status_code=resp.status_code, duration_ms=duration, store_id=self.store_id)
            if not resp.ok:
                ApiErrorLog.objects.create(message=f'Ozon error {resp.status_code}', payload=resp.text, store_id=self.store_id)
            return resp.json() if resp.text else {}
        except Exception as exc:
            ApiErrorLog.objects.create(message=str(exc), payload=str(payload), store_id=self.store_id)
            return {}
