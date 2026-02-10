#!/bin/bash

# 1. Запуск локального Redis (для Celery)
redis-server --daemonize yes

# 2. Применение миграций
python manage.py migrate

# 3. Запуск Celery в фоне
celery -A crm worker --loglevel=info --concurrency=1 &

# 4. Запуск Telegram бота в фоне
python bot/bot.py &

# 5. Запуск основного процесса Django (не в фоне!)
python manage.py runserver 0.0.0.0:8000