# avtoberg — рабочий MVP

Рабочий пользовательский сценарий:
**регистрация → вход → добавление магазина → реальная проверка ключей Ozon/WB → постановка initial sync в очередь → просмотр магазинов и заказов**.

## Что уже работает
- JWT-auth (Bearer token) с регистрацией и входом.
- Stores API: список + создание магазина.
- Реальная проверка подключения к API:
  - Ozon: запрос к Seller API.
  - Wildberries: запрос к Seller API.
- Initial sync job в Redis/RQ.
- Первый рабочий модуль данных: **Orders** (загрузка заказов при initial sync и выдача через `/api/v1/orders`).
- Frontend страницы:
  - `/register`, `/login` — формы и сохранение JWT.
  - `/stores` — загрузка списка, форма добавления магазина.
  - `/orders` — просмотр загруженных заказов.

## Что пока не реализовано
- Полноценные рабочие страницы: prices, fbo, analytics, stocks-returns.
- Production-hardening (ретраи, rate-limits, расширенный мониторинг, RBAC).

---

## 1) Локальная инфраструктура (PostgreSQL + Redis)

```bash
docker compose up -d
```

Проверка:
```bash
docker compose ps
```

## 2) Backend запуск

```bash
cd backend_fastapi
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Сгенерировать ключ шифрования (один раз) и вставить в `.env` (`CREDENTIAL_ENCRYPTION_KEY`):
```bash
python - <<'PY'
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
PY
```

Применить миграции:
```bash
alembic upgrade head
```

Запустить API:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 3) Worker запуск

В отдельном терминале:
```bash
cd backend_fastapi
source .venv/bin/activate
rq worker sync --url redis://localhost:6379/0
```

## 4) Frontend запуск

```bash
cd frontend_next
cp .env.example .env.local
npm install
npm run dev
```

Frontend: `http://localhost:3000`
Backend docs: `http://localhost:8000/docs`

## 5) Примеры запросов (curl)

Регистрация:
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"demo@example.com","password":"secret123"}'
```

Вход:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"demo@example.com","password":"secret123"}'
```

Создание магазина Ozon:
```bash
curl -X POST http://localhost:8000/api/v1/stores \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer <JWT_TOKEN>' \
  -d '{
    "name":"My Ozon Store",
    "marketplace":"ozon",
    "credentials":{"client_id":"<CLIENT_ID>","api_key":"<API_KEY>"}
  }'
```

Список магазинов:
```bash
curl -H 'Authorization: Bearer <JWT_TOKEN>' http://localhost:8000/api/v1/stores
```

Список sync jobs:
```bash
curl -H 'Authorization: Bearer <JWT_TOKEN>' http://localhost:8000/api/v1/sync-jobs
```

Список заказов:
```bash
curl -H 'Authorization: Bearer <JWT_TOKEN>' http://localhost:8000/api/v1/orders
```

## Поля для подключения магазина

### Ozon
- `client_id`
- `api_key`

### Wildberries
- `token`

> Ключи магазинов **не берутся из `.env`**: они вводятся пользователем в форме `/stores`, шифруются (Fernet) и сохраняются в таблице `api_credentials`.
> Из `.env`/секретов окружения читаются только системные параметры приложения (`SECRET_KEY`, `POSTGRES_DSN`, `REDIS_URL`, `CREDENTIAL_ENCRYPTION_KEY` и т.д.).
