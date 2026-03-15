# Frontend Next.js

```bash
cp .env.example .env.local
npm install
npm run dev
```

Логика:
- `/register` и `/login` вызывают backend API и сохраняют JWT в `localStorage`.
- Все запросы к защищенным endpoint идут с `Authorization: Bearer <token>`.
- После входа/регистрации редирект на `/stores`.
