# Backend FastAPI

## Запуск

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Worker

```bash
source .venv/bin/activate
rq worker sync --url redis://localhost:6379/0
```

## Миграции

```bash
alembic upgrade head
alembic downgrade -1
alembic revision -m "message" --autogenerate
```
