import os
from celery import Celery

# Устанавливаем настройки Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')

app = Celery('freelance_crm')

# Используем строку для конфигурации, чтобы воркеру не нужно было
# пиклевать объект настроек. Пространство имен 'CELERY' означает, что
# все настройки Celery в settings.py должны начинаться с этого префикса.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически ищем задачи (tasks.py) в приложениях
app.autodiscover_tasks()