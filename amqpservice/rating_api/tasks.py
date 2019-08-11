import pickle
import time

import redis
from celery import shared_task
from django.core.paginator import Paginator
from django.conf import settings

from rating_api.models import UserRatingView
from rating_api.utils.refresh_rating import refresh_rating


class KeyWriter:
    def __init__(self, connection):
        self.connection = connection
        self.current_key = connection.get('cache_key') \
            if connection.exists('cache_key') else 0
        self.previous_key = connection.get('previous_key') \
            if connection.exists('previous_key') else 0

    def write_new_key(self, new_key):
        previous_key_buffer = self.previous_key
        self.current_key, self.previous_key = new_key, self.current_key
        self._push_keys(previous_key_buffer)

    def _push_keys(self, key_for_delete):
        self.connection.set('cache_key', self.current_key)
        self.connection.set('previous_key', self.previous_key)
        if self.connection.exists(key_for_delete):
            self.connection.delete(key_for_delete)


def push_to_cache(page, cache_key, connection):
    objects = page.object_list
    if objects:

        def prepare_object(obj):
            return pickle.dumps(obj.dict_object), obj.dict_object['row']

        connection.zadd(
            cache_key,
            {row[0]: row[1] for row in map(prepare_object, objects)}
        )


@shared_task
def get_stored_objects():
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

    key_writer = KeyWriter(rating_board_cache)
    key_writer.write_new_key(new_cache_key)


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
        'schedule': 120,
    },
    'clear_redis_log': {
        'task': 'rating_api.tasks.clear_redis_log',
        'args': (),
        'options': {},
        'schedule': 600,
    },
}
