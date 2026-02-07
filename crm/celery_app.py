import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')

app = Celery('freelance_crm')

app.config_from_object('django.conf:settings', namespace='CELERY')

# Automatically search for tasks (tasks.py) in applications
app.autodiscover_tasks()