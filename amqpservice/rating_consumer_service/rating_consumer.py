import pytz
from django.conf import settings

import json
from datetime import datetime

from rating_api.models import UserRating
from rating_consumer_service.utils import PeriodicTimer, \
    DjangoRabbitCredsContainer
from rating_consumer_service.utils.connection_manager import \
    connection_manager


class MessageDict:
    def __init__(self):
        self.message_dict = {}
        self._update_list = []
        self._new_objects_list = None
        self._query = None

    def add_message(self, message_body):
        message_body = json.loads(message_body)

        key = message_body['user_id']
        new_message = UserRating(
            user_id=message_body['user_id'],
            rating=message_body['rating'],
            datetime=datetime.fromtimestamp(
                message_body['datetime'],
                tz=pytz.UTC
            )
        )
        current_message = self.message_dict.get(key)

        if not current_message \
                or current_message.datetime < new_message.datetime:
            self.message_dict[key] = new_message

    def _create_update_list(self):
        if self._query is None:
            self._query = UserRating.objects.filter(
                user_id__in=self.message_dict.keys()
            )
            print(self._query)
        for rated_user in self._query:
            bd_date = rated_user.datetime
            updated_user_id = rated_user.user_id
            updated_date = self.message_dict[updated_user_id].datetime
            updated_user = self.message_dict.pop(updated_user_id)
            if bd_date < updated_date:
                rated_user.rating = updated_user.rating
                rated_user.datetime = updated_user.datetime
                self._update_list.append(rated_user)

    def _create_new_objects_list(self):
        """
        Create a list of new objects.

        May be called only after _create_update_list.
        """
        self._new_objects_list = self.message_dict.values()
        print(self._new_objects_list)
        print(self._update_list)

    def _clear_data(self):
        self.message_dict.clear()
        self._update_list.clear()
        self._new_objects_list = None
        self._query = None

    def save_to_db(self):
        self._create_update_list()
        self._create_new_objects_list()
        if self._update_list:
            UserRating.objects.bulk_update(
                self._update_list,
                ('rating', 'datetime')
            )
        if self._new_objects_list:
            UserRating.objects.bulk_create(
                self._new_objects_list
            )
        self._clear_data()


def run_consumer():
    rabbit_credentials = DjangoRabbitCredsContainer()

    with connection_manager(rabbit_credentials.parameters) as connection:
        channel = connection.channel()
        channel.queue_declare(
            queue=rabbit_credentials.queue,
            durable=True,
            arguments={
                'x-max-priority': settings.RABBITMQ_X_MAX_PRIORITY,
            },
        )

        print(' [*] Waiting for messages. To exit press CTRL+C')

        message_dict = MessageDict()
        commit = type('Commit', (), {'status': False, })

        def callback(ch, method, properties, body):
            message_dict.add_message(body)
            print(body)
            if commit.status:
                ch.basic_ack(delivery_tag=method.delivery_tag, multiple=True)
                message_dict.save_to_db()
                commit.status = False

        channel.basic_qos(prefetch_count=0)
        channel.basic_consume(queue=settings.RABBITMQ_QUEUE_NAME,
                              on_message_callback=callback)

        timer = PeriodicTimer(5, setattr, (commit, 'status', True), {})
        timer.start()
        channel.start_consuming()


if __name__ == '__main__':
    run_consumer()
