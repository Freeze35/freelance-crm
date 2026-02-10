#!/bin/bash

# 1. Start local Redis (for Celery)
redis-server --daemonize yes

# 2. Apply migrations
python manage.py migrate

# 3. Start Celery in the background
celery -A crm worker --loglevel=info --concurrency=1 &

# 4. Start the Telegram bot in the background
python bot/bot.py &

# 5. Start the main Django process (not in the background!)
python manage.py runserver 0.0.0.0:8000