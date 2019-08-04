import pika

from django.conf import settings


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
