from django.db import models


class UserRating(models.Model):
    user_id = models.IntegerField(unique=True)
    rating = models.FloatField()
    datetime = models.DateTimeField()

    def __repr__(self):
        return f'UserRating user_id: {self.user_id} - ' \
               f'rating: {self.rating} - ' \
               f'datetime: {self.datetime}'

    def __str__(self):
        return f'UserRating user_id: {self.user_id} - ' \
               f'rating: {self.rating} - ' \
               f'datetime: {self.datetime}'


class RefreshLog(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    duration = models.DurationField()


class UserRatingView(models.Model):
    user_id = models.IntegerField(unique=True)
    rating = models.FloatField()
    datetime = models.DateTimeField()

    class Meta:
        managed = False

    def __repr__(self):
        return f'UserRating user_id: {self.user_id} - ' \
               f'rating: {self.rating} - ' \
               f'datetime: {self.datetime}'

    def __str__(self):
        return f'UserRating user_id: {self.user_id} - ' \
               f'rating: {self.rating} - ' \
               f'datetime: {self.datetime}'
