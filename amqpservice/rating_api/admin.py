from django.contrib import admin
from rating_api.models import UserRating, UserRatingView

admin.site.register(UserRating)
admin.site.register(UserRatingView)
