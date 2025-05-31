#!/bin/bash

echo "🔄 마이크로서비스 실행 중..."

SERVICES=(
    "auth_service:8001"
    "user_service:8002"
    "routine_service:8003"
    "scheduler_service:8004"
    "notification_service:8005"
    "letters_service:8006"
    "letter_storage_service:8007"
    "emotion_analysis:8008"
    "emotion_store_project:8009"
    "emotion_recommendation:8010"
    # "web-client:8011"
)

for entry in "${SERVICES[@]}"
do
    SERVICE_NAME="${entry%%:*}"
    PORT="${entry##*:}"

    if [ -d "$SERVICE_NAME" ]; then
        (
            cd "$SERVICE_NAME" || exit
            echo "▶️ $SERVICE_NAME 실행 (포트: $PORT)"
            nohup python manage.py runserver 0.0.0.0:$PORT > "../${SERVICE_NAME}.log" 2>&1 &
        )
    else
        echo "❌ 디렉토리 없음: $SERVICE_NAME"
    fi
done

echo "✅ 모든 서비스 실행 완료! 로그는 각 *.log 파일을 참조하세요."
