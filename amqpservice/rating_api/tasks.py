import time

from celery import shared_task
from celery.schedules import crontab


class TestEx(Exception):
    pass


@shared_task
def test_task():
    time.sleep(10)
    print('hello')
    raise TestEx


SCHEDULE = {
    'test_task': {
        'task': 'rating_api.tasks.test_task',
        'args': (),
        'options': {},
        'schedule': 5,
    },
}
