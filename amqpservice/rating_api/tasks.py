import time
from datetime import timedelta

import redis
from celery import shared_task


@shared_task
def hello():
    print('Hello there!')


@shared_task
def clear_redis_log():
    r = redis.Redis(host='redis', port=6379, db=2)

    keys = r.keys('*')
    for key in keys:
        r.delete(key)
    print('Clear redis log')


SCHEDULE = {
    'hello': {
        'task': 'rating_api.tasks.hello',
        'args': (),
        'options': {},
        'schedule': 5,
    },
    'clear_redis_log': {
        'task': 'rating_api.tasks.clear_redis_log',
        'args': (),
        'options': {},
        'schedule': 15,
    },
}
