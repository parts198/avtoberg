# Развёртывание на Timeweb (классическая панель)

## Подготовка окружения
1. В панели Timeweb откройте **Сайты** и убедитесь, что домен привязан к корневой папке `public_html`.
2. В разделе **Файл-менеджер** создайте папку `public_html/ozon_portal/`.
3. Скачайте проект локально и загрузите все файлы в `public_html/ozon_portal/` через FTP или веб-файл-менеджер. При обновлениях загружайте новый архив, распаковывайте рядом, затем атомарно переименовывайте папку, чтобы избежать downtime. Перед заменой сохраните резервную копию `db.sqlite3`.

## Настройка Python WSGI
1. В разделе **WWW** выберите пункт **Python**.
2. Создайте новое приложение, указав путь до каталога: `/home/<user>/public_html/ozon_portal`.
3. В поле **Entry point** задайте: `ozon_portal.wsgi:application`.
4. Выберите версию Python 3.10+ и сохраните. При изменении зависимостей повторно нажимайте «Перезапустить» в этом разделе.

## Установка зависимостей
Timeweb автоматически создаст виртуальное окружение для WSGI приложения. В консоли веб-панели выполните:
```
pip install -r public_html/ozon_portal/requirements.txt
python public_html/ozon_portal/manage.py migrate
python public_html/ozon_portal/manage.py collectstatic --noinput
```

## Cron-задачи
В разделе **Crontab** добавьте задания через мастер, выбирая интервал и команду вида:
```
python /home/<user>/public_html/ozon_portal/manage.py sync_products
python /home/<user>/public_html/ozon_portal/manage.py sync_warehouses
python /home/<user>/public_html/ozon_portal/manage.py sync_orders
python /home/<user>/public_html/ozon_portal/manage.py push_stocks
python /home/<user>/public_html/ozon_portal/manage.py sync_price_expense_snapshots
python /home/<user>/public_html/ozon_portal/manage.py recalc_price_metrics
python /home/<user>/public_html/ozon_portal/manage.py push_prices
python /home/<user>/public_html/ozon_portal/manage.py sync_finance_transactions
```

## Bootstrap администратора без SSH
1. В файле `.env` (создайте в корне проекта) задайте переменную `BOOTSTRAP_TOKEN=<секрет>` и `SECRET_KEY`.
2. Перезапустите WSGI приложение в панели.
3. Вызовите однократно endpoint `POST /api/admin/bootstrap/` с телом `{ "token": "<секрет>", "username": "admin", "password": "<пароль>", "email": "mail@example.com" }`.
4. После успешного вызова endpoint блокируется, создаётся администратор и записи `ExpensePolicySettings` со стратегией `USE_MAX`.

## Обновление проекта
- Загружайте новый релиз в новую папку, например `ozon_portal_new`, затем переименуйте старую в `ozon_portal_backup`, новую в `ozon_portal`. Перезапустите Python-приложение.
- Перед заменой копируйте `db.sqlite3` в надёжное место.

## Настройки
- Все конфигурации читаются из `.env` или переменных окружения (SECRET_KEY, DEBUG, BOOTSTRAP_TOKEN).
- БД — SQLite файл `db.sqlite3` в корне проекта.
- Логи пишутся в таблицы приложений `audit`.
