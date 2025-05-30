import logging
import json
from datetime import datetime
import os

from dotenv import load_dotenv
import openai
#from recommendation.feedback.models import Feedback

from .feedback.models import Feedback



# # 1. 현재 경로 확인
# print("📁 현재 파일 경로:", __file__)
# print("📁 현재 작업 디렉토리:", os.getcwd())

# # 2. 명시적으로 .env 경로 지정
# dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
# load_dotenv(dotenv_path)
# print("📄 .env 경로:", dotenv_path)

# # 3. 실제 환경변수 값
# print("🔑 OPENAI_API_KEY from os.environ:", os.environ.get("OPENAI_API_KEY"))
# print("🔑 OPENAI_API_KEY from dotenv only:", os.getenv("OPENAI_API_KEY"))

import os
openai.api_key = os.getenv("OPENAI_API_KEY")

# 로깅 설정 (최초 1회만 설정되도록)
logger = logging.getLogger("recommendation_logger")
if not logger.handlers:
    handler = logging.FileHandler("recommendation_logs.log", encoding="utf-8")
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    handler.setFormatter(formatter)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)


def log_recommendation(user_id, mood, recommendations):
    """
    추천 결과를 로그로 저장합니다.
    :param user_id: 사용자 ID
    :param mood: 분석된 감정
    :param recommendations: 추천 항목 리스트
    """
    data = {
        "user_id": user_id,
        "mood": mood,
        "recommendations": recommendations,
        "timestamp": datetime.utcnow().isoformat()
    }
    logger.info(json.dumps(data, ensure_ascii=False))

print("🔐 openai.api_key:", openai.api_key)

def get_recent_recommendations(user_id, limit=5):
    """
    사용자별 최근 추천 항목을 로그에서 추출합니다.
    :param user_id: 사용자 ID
    :param limit: 최대 추출할 추천 항목 수
    :return: 추천 항목 문자열들의 set
    """
    titles = []
    try:
        with open("recommendation_logs.log", encoding="utf-8") as f:
            lines = f.readlines()
            for line in reversed(lines):
                if f'"user_id": {user_id}' in line:
                    record = json.loads(line.split(" - ")[1])
                    titles.extend(record.get("recommendations", []))
                    if len(titles) >= limit:
                        break
    except FileNotFoundError:
        pass
    return set(titles[:limit])

def generate_recommendations(mood, user=None):

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": (
                    f"'{mood}' 감정을 가진 사람에게 추천할 "
                    f"대한민국 또는 외국 영화 3편과 음악 3곡을 각각 구분된 문단(예: '### 영화 추천' / '### 음악 추천') 아래에 항목별로 나열해줘. "
                    f"항목은 **숫자 없이** '제목 - 태그1, 태그2' 형식으로 한 줄씩 작성해줘. 중복 없이 제공해줘. "
                    f"예시:\n### 영화 추천\n기생충 - 드라마, 사회\n인셉션 - 스릴러, SF\n\n### 음악 추천\nDynamite - 팝, 댄스"
                ),
            },
        ],
        max_tokens=600
    )

    raw_text = response.choices[0].message.content
    lines = raw_text.strip().splitlines()
    parsed_lines = [line for line in lines if line and not line.startswith("###")]

    # 중복 제거
    if user:
        disliked_titles = set(
            Feedback.objects.filter(user=user, feedback="dislike")
            .values_list("item_title", flat=True)
        )
        recent_titles = get_recent_recommendations(user.id)
        parsed_lines = [
            line for line in parsed_lines
            if not any(dislike.strip() in line for dislike in disliked_titles)
            and line not in recent_titles
        ]

    return parsed_lines
