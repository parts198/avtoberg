FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY ozon_portal/requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY ozon_portal /app

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "ozon_portal.wsgi:application", "--bind", "0.0.0.0:8000", "--log-level", "debug"]
