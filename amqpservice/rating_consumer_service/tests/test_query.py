from django.test import TestCase

import time
from datetime import datetime
from random import random

from rating_api.models import UserRating


class ForTest(TestCase):
    def setUp(self) -> None:
        self._object_list = []
        for i in range(1, 11):
            UserRating.objects.create(
                user_id=i,
                rating=random(),
                datetime=datetime.fromtimestamp(time.time() - i)
            )

    def test_print(self):
        query = UserRating.objects.filter(user_id__in={2, 3})
        print(query)
        for i in query:
            print(i)
