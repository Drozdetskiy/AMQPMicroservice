import json

import pika

from django.conf import settings

from contextlib import contextmanager
from threading import Timer, Thread


class Message:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class MessageDict:
    def __init__(self):
        self.last_message_tag = None
        self._message_dict = {}

    def add_message(self, message_tag, message_body):
        message_body = json.loads(message_body)
        print(message_body)
        self.last_message_tag = message_tag

        key = message_body['user_id']
        new_message = Message(**message_body)
        current_message = self._message_dict.get(key)

        if not current_message \
                or current_message.datetime < new_message.datetime:
            self._message_dict[key] = new_message

    def clear(self):
        self._message_dict.clear()

    @property
    def keys(self):
        return self._message_dict.keys()

    @property
    def values(self):
        return self._message_dict.values()


class ReusableTimer(Timer):
    def reuse(self):
        new_timer = ReusableTimer(
            self.interval,
            self.function,
            self.args,
            self.kwargs
        )
        new_timer.start()
        return new_timer


class DjangoRabbitCredsContainer:
    def __init__(self):
        self.username = settings.RABBITMQ_USER
        self.password = settings.RABBITMQ_PASSWORD
        self.hostname = settings.RABBITMQ_HOST
        self.port = settings.RABBITMQ_PORT
        self.virtual_host = settings.RABBITMQ_VIRTUAL_HOST
        self.queue = settings.RABBITMQ_QUEUE_NAME

    @property
    def _credentials(self):
        return pika.PlainCredentials(self.username, self.password)

    @property
    def parameters(self):
        return pika.ConnectionParameters(
            host=self.hostname,
            port=self.port,
            virtual_host=self.virtual_host,
            credentials=self._credentials,
        )

    def __repr__(self):
        return f'Connector to Rabbit {self.username} on ' \
            f'host {self.hostname}:{self.port}'


@contextmanager
def connection_manager(parameters):
    connection = pika.BlockingConnection(parameters)
    try:
        yield connection
    finally:
        connection.close()
        print('Connection was closed')


def collect_with_timer(timer_sec, collect_func, args=(), kwargs=None):
    timer = ReusableTimer(timer_sec, collect_func, args, kwargs)
    timer.start()
    while True:
        if not timer.is_alive():
            timer = timer.reuse()


def collect():
    print('hello')


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

        def callback(ch, method, properties, body):
            message_dict.add_message(method.delivery_tag, body)

        channel.basic_qos(prefetch_count=10)
        channel.basic_consume(queue=settings.RABBITMQ_QUEUE_NAME,
                              on_message_callback=callback)

        channel.start_consuming(),
        timer_thread = Thread(
            target=collect_with_timer,
            args=(settings.RABBITMQ_COLLECT_TIME, collect)
        )

        timer_thread.start()


if __name__ == '__main__':
    run_consumer()
