import pika
from pika.channel import Channel
import pyarrow as pa
import pyarrow.parquet as pq
import pandas as pd
from ctakes_xml import CtakesXmlParser, CtakesXmlOutput
import json
from typing import Dict, List
import time

HDFS_PORT = 8020
HDFS_CLUSTER = 'mycluster'
HDFS_USER = 'cades'

RABBIT_HOST = '172.22.10.248'
RABBIT_PORT = 5672
QUEUE = 'mimic-parser'

max_buff_size = 10

fs = pa.hdfs.HadoopFileSystem(HDFS_CLUSTER, HDFS_PORT, user=HDFS_USER)

# pq_root_path = '/user/cades/mimic_parsed_output/'
pq_root_path = 'xml_benchmark'

class BufferedWriter(object):
    def __init__(self, max_buf_size):
        self.buffer = []
        self.max_buf_size = max_buf_size
        self.i = 0

    def cb(self):

        def callback(ch: Channel, method, properties, body: bytes):
            # TODO: Add logging message    
            xml_out: List = json.loads(body, encoding='utf-8')
            self.buffer.extend(xml_out)
            self.i += 1
            if self.i >= self.max_buf_size:
                df = pd.DataFrame(xml_out)
                table = pa.Table.from_pandas(df)
                pq.write_to_dataset(table, pq_root_path, filesystem = fs)
                self.i = 0
                self.buffer = []

            ch.basic_ack(delivery_tag=method.delivery_tag)
        return callback


creds = pika.PlainCredentials('cades', 'cades')
params = pika.ConnectionParameters(RABBIT_HOST, RABBIT_PORT, '/', creds)
conn = pika.BlockingConnection(params)
channel = conn.channel()
channel.queue_declare(queue=QUEUE)
channel.basic_qos(prefetch_count=1)

writer = BufferedWriter(max_buff_size)
channel.basic_consume(writer.cb(), queue=QUEUE, no_ack=False)

print("[x] waiting for messages...")
channel.start_consuming()



