from django.urls import path

from rating_api.views import TestView

urlpatterns = [
    path('', TestView.as_view(), name='test_view'),
]
