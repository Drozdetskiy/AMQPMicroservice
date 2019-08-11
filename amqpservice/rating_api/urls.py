from django.urls import path, re_path

from rating_api.views import TestView, LeaderBoardView, DetailRatingView

urlpatterns = [
    path('', TestView.as_view(), name='test_view'),
    re_path(
        r'leader_board/(?P<classifier>gt|lt)',
        LeaderBoardView.as_view(),
        name='leader_board_view'
    ),
    path(
        'leader_board/<int:position>',
        DetailRatingView.as_view(),
        name='detail_rating_view'
    ),
]
