import datetime
import time

from django.db import transaction, connection

from rating_api.models import RefreshLog


@transaction.atomic
def refresh_rating():
    start_time = time.monotonic()
    with connection.cursor() as cursor:
        cursor.execute(
            "REFRESH MATERIALIZED VIEW rating_api_userratingview"
        )
    end_time = time.monotonic()
    RefreshLog.objects.create(
        duration=datetime.timedelta(seconds=end_time - start_time)
    )
