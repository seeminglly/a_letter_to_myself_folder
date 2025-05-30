import openai
import json
from datetime import datetime
import os
from dotenv import load_dotenv
import requests

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")


def send_to_store_service(emotion_result: dict):
    try:
        response = requests.post(
            "http://localhost:8009/api/emotion-results/"  # 개발 환경 포트 기준
            json=emotion_result,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        print("✅ 감정 결과 저장 성공:", response.json())
    except requests.RequestException as e:
        print("❌ 감정 결과 저장 실패:", str(e))
        


def analyze_letter(letter):
    """
    단일 편지(letter) 딕셔너리에 대해 GPT 감정 분석을 수행하고 결과를 저장합니다.
    letter: {
        "letter_id": 3,
        "content": "오늘은 날씨가 맑고 기분이 상쾌했어요!",
        "user_id": 1
    }
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "너는 사람의 감정을 분석하는 감정 분석 AI야.\n"
                        "사용자의 편지 내용을 읽고, 대표 감정을 하나만 추출해줘.\n"
                        "감정은 반드시 아래의 카테고리 중 하나에서 골라야 해:\n\n"
                        "- 기쁨: 희열, 만족, 감사, 설렘\n"
                        "- 슬픔: 외로움, 상실감, 후회\n"
                        "- 분노: 짜증, 분개, 억울함\n"
                        "- 불안: 두려움, 긴장, 초조\n"
                        "- 사랑: 로맨스, 우정, 존경\n"
                        "- 중립: 해당 없음\n\n"
                        "출력은 반드시 다음 JSON 형식을 따라야 해:\n"
                        "{\n  \"mood\": \"기쁨\",\n  \"detailed_mood\": \"감사\"\n}\n"
                        "주의: 영어 감정(happy, sad 등)은 절대 사용하지 마. 반드시 한글로만 출력하고, 설명은 하지 마."
                    )
                },
                {
                    "role": "user",
                    "content": letter["content"]
                }
            ],
            max_tokens=50
        )

        content = response.choices[0].message.content.strip()
        emotion_data = json.loads(content)

        print(f"✅ 감정 분석 결과 - ID: {letter['letter_id']}, 감정: {emotion_data['mood']}, 세부감정: {emotion_data['detailed_mood']}")

        # ✅ emotion-store에 저장
       # 전송할 데이터 구성
        emotion_result = {
            "user": letter["user_id"],  # 🟡 사전에 포함되어 있어야 함
            "letter_id": letter["letter_id"],
            "dominant_emotion": emotion_data["mood"],
            "detailed_emotion": emotion_data["detailed_mood"],
            "emotion_scores": {emotion_data["mood"]: 1.0}  # 또는 실제 분석 결과 기반
        }
        send_to_store_service(emotion_result)

    except Exception as e:
        print(f"❌ 감정 분석 실패 (ID: {letter.get('letter_id', 'unknown')}): {e}")
