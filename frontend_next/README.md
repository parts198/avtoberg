# Frontend Next.js

```bash
cp .env.example .env.local
npm install
npm run dev
```

## API base URL

По умолчанию frontend работает в same-origin режиме через nginx reverse proxy:
- `NEXT_PUBLIC_API_URL=/api/v1`

Это позволяет браузеру обращаться к API через тот же origin (`http://IP/api/v1/...`),
без прямых запросов на `http://IP:8000`.

Логика:
- `/register` и `/login` вызывают backend API и сохраняют JWT в `localStorage`.
- Все запросы к защищенным endpoint идут с `Authorization: Bearer <token>`.
- После входа/регистрации редирект на `/stores`.
