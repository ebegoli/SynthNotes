import pika
import pyarrow as pa
import time


HDFS_PORT = 8020
HDFS_CLUSTER = 'mycluster'
HDFS_USER = 'cades'

RABBIT_HOST = '172.22.10.248'
RABBIT_PORT = 5672
QUEUE = 'mimic-files'
EXCHANGE = ''

n_files = 100000

ctakes_xml_dir = '/user/cades/ctakes/output/'


fs = pa.hdfs.HadoopFileSystem(HDFS_CLUSTER, HDFS_PORT, user=HDFS_USER)
files = fs.ls(ctakes_xml_dir)

creds = pika.PlainCredentials('cades', 'cades')
params = pika.ConnectionParameters(RABBIT_HOST, RABBIT_PORT, '/', creds)
conn = pika.BlockingConnection(params)
channel = conn.channel()
q = channel.queue_declare(queue=QUEUE)


for f in files[:n_files]:
    channel.basic_publish(exchange=EXCHANGE, routing_key=QUEUE, body=f)

time.sleep(1)
start = time.time()

while q.method.message_count > 0:
    print(f'queue has {q.method.message_count} messages...')
    time.sleep(0.5)
    q = channel.queue_declare(queue=QUEUE)

end = time.time()
print(f"Parsing took {end - start} seconds")

conn.close()
