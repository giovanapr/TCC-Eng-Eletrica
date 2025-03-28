from is_wire.core import Channel, Subscription, Message, Logger, Tracer, AsyncTransport
from is_msgs.image_pb2 import Image
import numpy as np
import cv2
import json
import time
import re
import socket
from opencensus.trace.span import Span
from opencensus.ext.zipkin.trace_exporter import ZipkinExporter

def create_exporter(service_name: str, uri: str, log: Logger) -> ZipkinExporter:
    zipkin_ok = re.match("http:\\/\\/([a-zA-Z0-9\\.]+)(:(\\d+))?", uri)
    if not zipkin_ok:
        log.critical('Invalid zipkin uri "{}", expected http://<hostname>:<port>', uri)
    exporter = ZipkinExporter(
        service_name=service_name,
        host_name=zipkin_ok.group(1), # type: ignore[union-attr]
        port=zipkin_ok.group(3), # type: ignore[union-attr]
        transport=AsyncTransport,
    )
    return exporter

def span_duration_ms(span: Span) -> float:
    dt = dp.parse(span.end_time) - dp.parse(span.start_time)
    return dt.total_seconds() * 1000.0

def to_np(input_image):
    if isinstance(input_image, np.ndarray):
        output_image = input_image
    elif isinstance(input_image, Image):
        buffer = np.frombuffer(input_image.data, dtype=np.uint8)
        output_image = cv2.imdecode(buffer, flags=cv2.IMREAD_COLOR)
    else:
        output_image = np.array([], dtype=np.uint8)
    return output_image

service_name = "Consume.Image"
log = Logger(name=service_name)

exporter = create_exporter(
        service_name=service_name,
        uri="http://10.10.2.211:30200",
        log=log,
    )

#Connect to the broker
channel = Channel(f"amqp://guest:guest@10.10.2.211:30000")
log.info(f"Created channel - amqp://guest:guest@10.10.2.211:30000")

if __name__ == '__main__':

    subscription = Subscription(channel)
    subscription.subscribe(topic="Topic.Frame")

    while True:
        log.info("Waiting for Images")

        msg = channel.consume()

        timestamp_rcvd = time.time()

        msg_contrace = (
            f'{{"timestamp_send": "{int(msg.created_at*1000000)}", '
            f'"timestamp_rcvd": "{int(timestamp_rcvd*1000000)}", '
            f'"x-b3-flags": "{msg.metadata["x-b3-flags"]}", '
            f'"x-b3-parentspanid": "{msg.metadata["x-b3-parentspanid"]}", '
            f'"x-b3-sampled": "{msg.metadata["x-b3-sampled"]}", '
            f'"x-b3-spanid": "{msg.metadata["x-b3-spanid"]}", '
            f'"x-b3-traceid": "{msg.metadata["x-b3-traceid"]}", '
            f'"spanname": "frame"}}'
        )
        bytesToSend = str.encode(msg_contrace)

        serverAddressPort = ("10.10.2.211", 31589)
        bufferSize = 2048

        UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        log.info("Enviando mensagem para Contrace")
        UDPClientSocket.sendto(bytesToSend, serverAddressPort)
        log.info("Mensagem para Contrace: {}", msg_contrace)

        tracer = Tracer(exporter=exporter, span_context=msg.extract_tracing())

        with tracer.span(name='unpack_and_save_image'):
            img_unpack = msg.unpack(Image)
            imNP = to_np(img_unpack)
            filename = './image_rcvd.jpg'
            log.info("Image saved")
