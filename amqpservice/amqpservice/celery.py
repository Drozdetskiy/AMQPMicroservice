from __future__ import absolute_import, unicode_literals
import os

import django
from celery import Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'amqpservice.settings')

app = Celery('amqpservice')
django.setup()

from rating_api.tasks import SCHEDULE as RATING_API_SCHEDULE

app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.beat_schedule = RATING_API_SCHEDULE
app.autodiscover_tasks()
