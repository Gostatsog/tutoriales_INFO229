#!/usr/bin/env python
import pika
import sys
from googleapiclient.discovery import build

api_key = ''

class Yutupi:
      #Constructor
      def __init__(self,channel):
         self.channel = channel

     #Buscar dato
      def buscarCanal(channel=""):
         youtube = build('youtube','v3',developerKey=api_key)
         
         request = youtube.channels().list(
            part = 'statistics',
            forUsername=channel)
         response = request.execute()
         print(response)


connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='direct_logs', exchange_type='direct')

result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

#for severity in severities:
channel.queue_bind(exchange='direct_logs', queue=queue_name, routing_key='Ytb')

print(' [*] Waiting for logs. To exit press CTRL+C')


def callback(ch, method, properties, body):
    Yutupi.buscarCanal(body)


channel.basic_consume(
    queue=queue_name, on_message_callback=callback, auto_ack=True)

channel.start_consuming()
