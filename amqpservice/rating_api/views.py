import redis
from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView


class TestView(APIView):
    def get(self, request):
        r = redis.Redis(host='redis', port=6379, db=2)
        keys = r.keys('*')
        res = []
        for i in keys:
            res.append(r.get(i))
        return Response(res)
