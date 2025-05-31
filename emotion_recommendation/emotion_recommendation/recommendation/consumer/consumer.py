# recommendation/consumer.py

import pika, json
import django
import os

# Django 설정 초기화
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "emotion_recommendation.settings") 
django.setup()

# 예: emotion_recommendation/recommendation/consumer.py

from recommendation.utils import log_recommendation, get_recent_recommendations, generate_recommendations
def start_consumer():
    credentials = pika.PlainCredentials("myuser", "mypassword")  # ← 실제 사용자명과 비밀번호 사용
    parameters = pika.ConnectionParameters(
        host="34.47.116.44",       # RabbitMQ 외부 IP
        port=5672,
        virtual_host="/",
        credentials=credentials
    )

    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    # 익스체인지/큐 선언 및 바인딩
    channel.exchange_declare(exchange='recommendation.direct', exchange_type='direct')
    channel.queue_declare(queue='recommendation.queue', durable=True)
    channel.queue_bind(exchange='recommendation.direct', queue='recommendation.queue', routing_key='recommend')

    channel.basic_consume(queue='recommendation.queue', on_message_callback=callback, auto_ack=True)
    print("🎧 [*] Waiting for messages...")
    channel.start_consuming()


def callback(ch, method, properties, body):
    data = json.loads(body)
    user_id = data["user"]
    mood = data["mood"]

    print(f"📥 메시지 수신: user={user_id}, mood={mood}")

    # GPT를 통한 추천 생성
    recommendations = generate_recommendations(mood)

    # 중복 제거 및 로그 기록
    recent = get_recent_recommendations(user_id)
    filtered = [r for r in recommendations if r not in recent]
    log_recommendation(user_id, mood, filtered)

    print("✅ 추천 처리 완료")


if __name__ == "__main__":
    start_consumer()
