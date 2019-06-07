import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'btk2.settings')

celery_app = Celery('btk2')
celery_app.config_from_object('django.conf:settings')
celery_app.autodiscover_tasks()
