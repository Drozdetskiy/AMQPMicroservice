from django.db import models


class UserRating(models.Model):
    user_id = models.IntegerField(unique=True)
    rating = models.FloatField()
    datetime = models.DateTimeField()

    def __repr__(self):
        return f'UserRating user_id: {self.user_id} - ' \
               f'rating: {self.rating} - ' \
               f'datetime: {self.datetime}'
