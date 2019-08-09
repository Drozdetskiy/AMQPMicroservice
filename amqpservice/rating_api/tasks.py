import time
from datetime import timedelta

from celery import shared_task


@shared_task
def hello():
    print('Hello there!')
