import pika

from contextlib import contextmanager


@contextmanager
def connection_manager(parameters):
    connection = pika.BlockingConnection(parameters)
    try:
        yield connection
    finally:
        connection.close()
        print('Connection was closed')