# Ozon Margin Dashboard

API-first dashboard для расчёта юнит-экономики, синков Ozon Seller API и сравнения факт/план по заказам.

## Стек
- Next.js (App Router, TypeScript)
- PostgreSQL + Prisma
- Redis + BullMQ
- TailwindCSS
- Pino logging

## Требования
- Node.js 20+
- Docker + Docker Compose
- PostgreSQL 15+
- Redis 7+

## Быстрый старт (dev)
```bash
cp .env.example .env

docker compose up -d db redis
npm ci
npx prisma migrate dev
npx prisma db seed
npm run dev
```

Отдельный worker:
```bash
npm run worker
```

## Прод (Ubuntu + Fastpanel)
### 1) Установка Docker
```bash
sudo apt update
sudo apt install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

cat <<'DOCKERLIST' | sudo tee /etc/apt/sources.list.d/docker.list
 deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable
DOCKERLIST

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

### 2) Установка проекта
```bash
sudo mkdir -p /opt/ozon-margin-dashboard
sudo chown $USER:$USER /opt/ozon-margin-dashboard
cd /opt/ozon-margin-dashboard

git clone <YOUR_REPO_URL> .
cp .env.example .env
```

Заполните `.env`:
- `POSTGRES_PASSWORD`
- `DATABASE_URL`
- `REDIS_URL`
- `MASTER_KEY` (base64 32 bytes)
- `ADMIN_LOGIN` / `ADMIN_PASSWORD`

### 3) Запуск
```bash
docker compose -f docker-compose.prod.yml up -d --build
```

### 4) Миграции/сид
```bash
docker compose -f docker-compose.prod.yml exec web npx prisma migrate deploy

docker compose -f docker-compose.prod.yml exec web npx prisma db seed
```

### 5) Проверка
```bash
docker compose -f docker-compose.prod.yml ps

docker compose -f docker-compose.prod.yml logs -f web
curl http://127.0.0.1:3000
```

### Fastpanel (Reverse proxy)
- Создайте сайт и включите Reverse proxy
- Upstream: `http://127.0.0.1:3000`
- SSL: Let's Encrypt

## Обновления (prod)
```bash
cd /opt/ozon-margin-dashboard

git pull

docker compose -f docker-compose.prod.yml up -d --build

docker compose -f docker-compose.prod.yml exec web npx prisma migrate deploy
```

## Бэкап и восстановление
```bash
# backup
pg_dump -h 127.0.0.1 -U postgres -d ozon_dashboard > backup.sql

# restore
psql -h 127.0.0.1 -U postgres -d ozon_dashboard < backup.sql
```

## Операционный чеклист
- Запуск: `docker compose up -d db redis` + `npm run dev`
- Добавить магазин: раздел **Магазины** → заполнить Client-Id и Api-Key → нажать **Проверить подключение**
- Форсировать синк: пока вручную через worker/queue (заготовка есть в `src/jobs/worker.ts`)

## Структура
```
/
  README.md
  docker-compose.yml
  docker-compose.prod.yml
  .env.example
  /docs
  /prisma
  /src
```

