import pytz
from django.test import TestCase

import time
import random
from datetime import datetime

from rating_api.models import UserRating, UserRatingView
from rating_api.utils.refresh_rating import refresh_rating


class QueryTest(TestCase):
    def setUp(self) -> None:
        self._object_list = []
        for i in range(1, 11):
            UserRating.objects.create(
                user_id=i,
                rating=random.randint(1, 2),
                datetime=datetime.fromtimestamp(time.time() - i, tz=pytz.UTC)
            )

    def test_print(self):
        refresh_rating()
        query = UserRatingView.objects.order_by('-rating', 'datetime')
        for i in query:
            print(i)
