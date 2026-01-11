# Ozon Seller API

## Авторизация
Все запросы отправляются на `https://api-seller.ozon.ru` и должны содержать заголовки:
- `Client-Id`: идентификатор продавца
- `Api-Key`: ключ API
- `Content-Type: application/json`
- `Accept: application/json`

Ключи хранятся в БД в зашифрованном виде (AES-256-GCM). Мастер-ключ задаётся в `MASTER_KEY` (base64, 32 bytes).

## Используемые эндпоинты
1. **Проверка подключения**
   - `POST /v1/warehouse/list`
2. **Цены**
   - `POST /v4/product/info/prices` (до 1000 товаров за запрос)
3. **Остатки**
   - `POST /v2/analytics/stock_on_warehouses` (две выборки: `FBS` и `FBO`)
4. **Заказы**
   - `POST /v3/posting/fbs/list` (пагинация offset/has_next)
5. **Начисления**
   - `POST /v3/finance/transaction/list` (период не более 1 месяца; батчи 1–7 дней)

## Ограничения
- `transaction/list` ограничивает период (1 месяц). Используйте батчи.
- `product/info/prices` ограничивает список товарами (до 1000).
- Повторяющиеся запросы должны быть идемпотентными (upsert по ключам).

## Примеры запросов
```json
POST /v1/warehouse/list
{}
```

```json
POST /v3/finance/transaction/list
{
  "filter": {
    "date": { "from": "2024-01-01T00:00:00.000Z", "to": "2024-01-07T23:59:59.000Z" },
    "posting_number": "123-456"
  },
  "page": 1,
  "page_size": 1000
}
```
