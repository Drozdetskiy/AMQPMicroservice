import pickle

import redis

from django.conf import settings
from django.utils.datastructures import MultiValueDictKeyError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class RedisConnectionMixin:
    connection = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_BOARD_DB
    )


# Create your views here.
class TestView(APIView, RedisConnectionMixin):
    def get(self, request):
        cache_key = self.connection.get('cache_key')
        res = self.connection.zrange(cache_key, 0, 0, withscores=True)
        print(res, self.connection.keys('*'))
        return Response('ok')


class LeaderBoardView(APIView, RedisConnectionMixin):
    def get(self, request, classifier):
        try:
            position = request.GET['position']
            page_len = request.GET['page_len']
            page = request.GET['page']
        except MultiValueDictKeyError:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response((classifier, position, page_len, page))


class DetailRatingView(APIView, RedisConnectionMixin):
    def get(self, request, position):
        cache_key = self.connection.get('cache_key')
        if not position:
            return Response(status=status.HTTP_404_NOT_FOUND)

        raw_res = self.connection.zrange(
            cache_key,
            position - 2 if position > 1 else 0,
            position,
        )
        res = map(pickle.loads, raw_res)

        return Response(res)
