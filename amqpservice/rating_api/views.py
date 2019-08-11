import redis
from django.conf import settings
from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView

from rating_api.models import UserRatingView


class TestView(APIView):
    def get(self, request):
        # r = redis.Redis(host='redis', port=6379, db=1)
        # res = r.zrange(settings.REDIS_LEADER_SET_NAME, 0, -1, withscores=True)
        # r = redis.StrictRedis(host='redis', port=6379, db=1)
        # r.flushdb()
        res = UserRatingView.objects.first()
        return Response(int(res.row))
