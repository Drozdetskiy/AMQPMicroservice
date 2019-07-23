import os
import ssl

import pika

from time import sleep


username = os.getenv('RABBITMQ_USER')
password = os.getenv('RABBITMQ_PASSWORD')
hostname = os.getenv('RABBITMQ_HOST')
port = int(os.getenv('RABBITMQ_PORT'))
print(username)
print(password)
print(hostname)
print(port)
credentials = pika.PlainCredentials(username, password)
parameters = pika.ConnectionParameters('rabbitmq',
                                       port,
                                       '/',
                                       credentials
                                       )

sleep(7)

connection = pika.BlockingConnection(parameters)
channel = connection.channel()
channel.queue_declare(queue='hello')

while True:
    channel = connection.channel()

    channel.basic_publish(
        exchange='',
        routing_key='hello',
        body='Hello World!'
    )
    print(" [x] Sent 'Hello World!'")
    sleep(1)
