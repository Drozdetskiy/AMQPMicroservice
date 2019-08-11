import redis
from django.conf import settings
from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView

from rating_api.models import UserRatingView


class TestView(APIView):
    def get(self, request):
        r = redis.Redis(host='redis', port=6379, db=settings.REDIS_BOARD_DB)
        cache_key = r.get('cache_key')
        res = r.zrange(cache_key, 0, 5, withscores=True)
        print(res, r.keys('*'))
        r = redis.StrictRedis(host='redis', port=6379, db=1)
        return Response('ok')
