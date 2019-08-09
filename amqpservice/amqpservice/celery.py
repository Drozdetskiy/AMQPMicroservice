from __future__ import absolute_import, unicode_literals
import os

from celery import Celery
from rating_api.tasks import SCHEDULE as RATING_API_SCHEDULE
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'amqpservice.settings')

app = Celery('amqpservice')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.beat_schedule = RATING_API_SCHEDULE
app.autodiscover_tasks()
