#!/usr/bin/env python
import wikipedia
import pageviewapi
import pymongo
import os
import pika
import sys

DATABASE = "wiki"
COLLECTION = "wikicol"               

class wikiPod:
     #Constructor
      def __init__(self,channel):
         self.channel = channel

     #Buscar dato
      def buscarDato(dat="Programming"):
         w = wikipedia.page(dat)
         print(w.content)

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='direct_logs', exchange_type='direct')

result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

#for severity in severities:
channel.queue_bind(exchange='direct_logs', queue=queue_name, routing_key='Wiki')

print(' [*] Waiting for logs. To exit press CTRL+C')


def callback(ch, method, properties, body):
    wikiPod.buscarDato(body)


channel.basic_consume(
    queue=queue_name, on_message_callback=callback, auto_ack=True)

channel.start_consuming()



