"""Adapters around legacy Python scripts.

Здесь подключаются существующие python-скрипты аналитики продаж и остатков/возвратов
как отдельные сервисы.
"""


def run_sales_analytics(*args, **kwargs):
    return {'status': 'in_progress', 'data': []}


def run_stocks_returns_analytics(*args, **kwargs):
    return {'status': 'in_progress', 'data': []}
