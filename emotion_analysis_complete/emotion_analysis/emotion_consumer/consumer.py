# consumer.py
import pika
import json
from .analyze import analyze_letter
def start_consumer():
    credentials = pika.PlainCredentials('myuser', 'mypassword')
    parameters = pika.ConnectionParameters(
        host='34.47.117.180',
        port=5672,
        virtual_host='/',
        credentials=credentials
    )
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    channel.exchange_declare(exchange='emotion.direct', exchange_type='direct')
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange='emotion.direct', queue=queue_name, routing_key='analyze')

    def callback(ch, method, properties, body):
        letter = json.loads(body)
        print(f"📩 수신한 편지: {letter}")
        analyze_letter(letter)  
    print("🎧 메시지 수신 대기 중...")
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()