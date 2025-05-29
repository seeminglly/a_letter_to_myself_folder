import json
import requests
import pika
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(["POST"])
# @permission_classes([IsAuthenticated])
def reanalyze_all_emotions(request):
    """REST API를 통해 letter-service에서 편지 5개 가져와 RabbitMQ로 발행"""
    user = request.user
    # 대신 더미 데이터 사용
    # letters_data = [
    #     {"id": 1, "content": "요즘 날씨가 좋아서 기분이 좋다."},
    #     {"id": 2, "content": "오늘은 우울한 하루였다."},
    #     {"id": 3, "content": "시험 공부가 너무 힘들다."},
    #     {"id": 4, "content": "친구와 여행 계획을 짰다."},
    #     {"id": 5, "content": "가족과 함께 보내는 시간은 소중하다."},
    # ]
    try:
        # ✅ 1. letter-service에서 최근 편지 5개 가져오기
        response = requests.get(
            "http://localhost:8000/api/letters/",
            headers={"Authorization": f"Bearer {request.auth}"}
        )
        response.raise_for_status()
        letters_data = response.json()[:5]

        # ✅ 2. RabbitMQ 연결 설정
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        channel.exchange_declare(exchange='emotion.direct', exchange_type='direct')

        # ✅ 3. 각 편지를 MQ로 발행
        for letter in letters_data:
            message = {
                "letter_id": letter["id"],
                "content": letter["content"]
            }
            channel.basic_publish(
                exchange='emotion.direct',
                routing_key='analyze',  # direct exchange에서 routing key 사용
                body=json.dumps(message),
            )

        connection.close()

        return Response({"status": "success", "published_count": len(letters_data)})

    except requests.RequestException as e:
        return Response({"error": "편지를 불러오는 데 실패했습니다", "details": str(e)}, status=500)
    except pika.exceptions.AMQPError as e:
        return Response({"error": "RabbitMQ로 발행 실패", "details": str(e)}, status=500)

