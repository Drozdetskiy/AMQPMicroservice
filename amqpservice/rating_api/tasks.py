import pickle
import time
from datetime import timedelta

import redis
from celery import shared_task
from celery.schedules import crontab
from django.core.paginator import Paginator
from django.conf import settings

from rating_api.models import UserRatingView
from rating_api.utils.refresh_rating import refresh_rating


def push_to_cache(page, cache_key, connection):
    objects = page.object_list
    if objects:
        def prepare_object(obj):
            return f'{obj.dict_object["row"]}:' \
                   f'{obj.dict_object["user_id"]}:' \
                   f'{obj.dict_object["rating"]}',\
                      obj.dict_object['row']

        user_rating_map = map(prepare_object, objects)
        for user_rating in user_rating_map:
            connection.zadd(cache_key, {user_rating[0]: user_rating[1]})


@shared_task
def get_stored_objects():
    now = time.time()
    refresh_rating()
    rating_board = UserRatingView.objects.order_by('id')
    rating_paginator = Paginator(rating_board, settings.CELERY_PAGE_LEN)
    new_cache_key = time.time()
    rating_board_cache = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_BOARD_DB,
    )

    for page_number in rating_paginator.page_range:
        page = rating_paginator.page(page_number)
        push_to_cache(page, new_cache_key, rating_board_cache)

    if rating_board_cache.exists('cache_key'):
        previous_key = rating_board_cache.get('cache_key')
        rating_board_cache.set('cache_key', new_cache_key)
        rating_board_cache.delete(previous_key)
    else:
        rating_board_cache.set('cache_key', new_cache_key)

    print('#' * 20, time.time() - now)


@shared_task
def clear_redis_log():
    r = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_RESULT_BACKEND_DB,
    )

    keys = r.keys('*')
    for key in keys:
        r.delete(key)
    print('Clear redis log')


SCHEDULE = {
    'get_stored_objects': {
        'task': 'rating_api.tasks.get_stored_objects',
        'args': (),
        'options': {},
        'schedule': 30,
    },
    'clear_redis_log': {
        'task': 'rating_api.tasks.clear_redis_log',
        'args': (),
        'options': {},
        'schedule': crontab(),
    },
}
