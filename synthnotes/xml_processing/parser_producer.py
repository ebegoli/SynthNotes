import pika
from pika.channel import Channel
import pyarrow as pa
from ctakes_xml import CtakesXmlParser
import json
from typing import Dict, List


HDFS_PORT = 8020
HDFS_CLUSTER = 'mycluster'
HDFS_USER = 'cades'

RABBIT_HOST = '172.22.10.248'
RABBIT_PORT = 5672
QUEUE_FILES = 'mimic-files'
QUEUE_PARSER = 'mimic-parser'
EXCHANGE = ''

ctakes_xml_dir = '/user/cades/ctakes/output/'

fs = pa.hdfs.HadoopFileSystem(HDFS_CLUSTER, HDFS_PORT, user=HDFS_USER)

creds = pika.PlainCredentials('cades', 'cades')
params = pika.ConnectionParameters(RABBIT_HOST, RABBIT_PORT, '/', creds)

parser = CtakesXmlParser()


def callback_files(ch: Channel, method, properties, body):
 #   print(f'received msg to parge {body}')

    output = ''
    with fs.open(body, 'rb') as xml_file:
        # parse xml file
        result = parser.parse(xml_file)
        # for k in result.keys():
        #     result[k] = list(result[k])
        # # serialize output dict
        output = json.dumps(result)
        
    # publish output
    channel_parser.basic_publish(exchange=EXCHANGE, routing_key=QUEUE_PARSER, body=output)
    ch.basic_ack(delivery_tag=method.delivery_tag)


conn_parser = pika.BlockingConnection(params)
channel_parser = conn_parser.channel()
channel_parser.queue_declare(queue=QUEUE_PARSER)

conn_files = pika.BlockingConnection(params)
channel_files = conn_files.channel()
channel_files.queue_declare(queue=QUEUE_FILES)

channel_files.basic_qos(prefetch_count=1)
channel_files.basic_consume(callback_files, queue=QUEUE_FILES, no_ack=False)



print("[x] waiting for messages...")
channel_files.start_consuming()


