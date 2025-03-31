from is_wire.core import Channel, Subscription, Message, Logger, AsyncTransport, Tracer
from opencensus.ext.zipkin.trace_exporter import ZipkinExporter
from opencensus.trace.span_context import SpanContext, generate_trace_id
from opencensus.trace import tracer
from is_msgs.image_pb2 import Image
import cv2
import numpy as np
import time
import re
import random
#------------#
import socket
import pickle
#------------#

def to_image(input_image, encode_format='.jpeg', compression_level=0.8):
    if isinstance(input_image, np.ndarray):
        if encode_format == '.jpeg':
            params = [cv2.IMWRITE_JPEG_QUALITY, int(compression_level * (100 - 0) + 0)]
        elif encode_format == '.png':
            params = [cv2.IMWRITE_JPEG_COMPRESSION, int(compression_level * (9 - 0) + 0)]
        else:
            return Image()
        cimage = cv2.imencode(ext=encode_format, img=input_image, params=params)
        return Image(data=cimage[1].tobytes())
    elif isinstance(input_image, Image):
        return input_image
    else:
        return Image()

service_name = "Pub.Images"
log = Logger(name=service_name)
#----------------------------------------------------------------#
HOST = "10.10.2.1"
PORT = 20000
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
log.info(f'Socket created {HOST}:{PORT}')
#----------------------------------------------------------------#

exporter = ZipkinExporter(
    service_name=service_name,
    host_name="10.10.2.211",
    port=30200,
    transport=AsyncTransport,
    )

channel = Channel(f'amqp://guest:guest@10.10.2.211:30000')
log.info(f"Created channel - amqp://guest:guest@10.10.2.211:30000")

aux = 0

while True:
    tracer = Tracer(exporter=exporter)

    log.info("Indicate Directory and file Image")
    img_caminho = input('Directory and file Image: ')

    with tracer.span(name="frame") as span:
        img = cv2.imread(img_caminho)
        img_msg = Message()
        img_msg.pack(to_image(img))
        img_msg.inject_tracing(span)

    img_msg.created_at = time.time()

    if aux<10:
        channel.publish(img_msg, topic='Topic.Frame')
        log.info('Message sent via pub/sub')
    else:
        data = pickle.dumps(img_msg)
        client_socket.sendto(data, (HOST, PORT))
        log.info('Message sent via socket')

    aux = aux + 1
