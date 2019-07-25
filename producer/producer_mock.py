import pika

from contextlib import contextmanager
from time import sleep
from os import getenv


class RabbitCredsContainer:
    def __init__(self):
        self.username = getenv('RABBITMQ_USER', 'guest')
        self.password = getenv('RABBITMQ_PASSWORD', 'guest')
        self.hostname = getenv('RABBITMQ_HOST', 'localhost')
        self.port = int(getenv('RABBITMQ_PORT', '5672'))
        self.virtual_host = getenv('RABBITMQ_VIRTUAL_HOST', '/')
        self.queue = getenv('RABBITMQ_USER_NAME', 'test_queue')

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


def ping_message(channel, message, queue, time=1):
    while True:
        channel.basic_publish(
            exchange='',
            routing_key=queue,
            body=message
        )
        print(f" [x] Sent {message}")
        sleep(time)


def generate_message():
    return 'test message'


if __name__ == '__main__':
    rabbit_credentials = RabbitCredsContainer()

    with connection_manager(rabbit_credentials.parameters) as connection:
        channel = connection.channel()
        channel.queue_declare(queue=rabbit_credentials.queue)
        message = generate_message()
        ping_message(channel, message, queue=rabbit_credentials.queue)
