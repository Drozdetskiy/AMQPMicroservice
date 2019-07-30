import pika
from pika import BasicProperties

import json
import time
import random
from contextlib import contextmanager
from os import getenv


class ProducerConfig:
    X_MAX_PRIORITY = 10
    MESSAGE_PRIORITY = 3
    MESSAGE_PING_RATE = 1
    PLAYER_MAX_ID = 3000000
    PLAYER_RATING_ORDER = 5


class RabbitCredsContainer:
    def __init__(self):
        self.username = getenv('RABBITMQ_USER', 'guest')
        self.password = getenv('RABBITMQ_PASSWORD', 'guest')
        self.hostname = getenv('RABBITMQ_HOST', 'localhost')
        self.port = int(getenv('RABBITMQ_PORT', '5672'))
        self.virtual_host = getenv('RABBITMQ_VIRTUAL_HOST', '/')
        self.queue = getenv('RABBITMQ_QUEUE_NAME', 'test_queue')

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


class User:
    def __init__(self, user_id=None, rating=None, datetime=None):
        self.user_id = user_id if user_id is not None else random.randint(
            0, ProducerConfig.PLAYER_MAX_ID
        )
        self.rating = rating if rating is not None else round(
            random.random(),
            ProducerConfig.PLAYER_RATING_ORDER
        )
        self.datetime = datetime or int(time.time())

    def get_info(self):
        return json.dumps(
            {
                'user_id': self.user_id,
                'rating': self.rating,
                'datetime': self.datetime,
            }
        )

    def __repr__(self):
        return f'User: {self.user_id} - {self.rating} - {self.datetime}'


@contextmanager
def connection_manager(parameters):
    connection = pika.BlockingConnection(parameters)
    try:
        yield connection
    finally:
        connection.close()
        print('Connection was closed')


def ping_message(channel, message, queue):
    channel.basic_publish(
        exchange='',
        routing_key=queue,
        body=message,
        properties=BasicProperties(priority=ProducerConfig.MESSAGE_PRIORITY)
    )


def generate_message():
    return User().get_info()


def run_mock():
    rabbit_credentials = RabbitCredsContainer()

    with connection_manager(rabbit_credentials.parameters) as connection:
        channel = connection.channel()
        channel.queue_declare(
            queue=rabbit_credentials.queue,
            durable=True,
            arguments={'x-max-priority': ProducerConfig.X_MAX_PRIORITY},
        )

        while True:
            message = generate_message()
            ping_message(channel, message, queue=rabbit_credentials.queue)
            time.sleep(ProducerConfig.MESSAGE_PING_RATE)


if __name__ == '__main__':
    run_mock()
