import openai
from django.utils.timezone import now
import json

def analyze_emotion_for_letter(letter):
    """
    편지 내용을 GPT에게 분석시켜 감정을 상위/하위로 분리해서 저장.
    예: mood='슬픔', detailed_mood='후회'
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
                    "content": letter.content
                }
            ],
            max_tokens=50
        )

        # 응답 파싱
        content = response.choices[0].message.content.strip()
        emotion_data = json.loads(content)

        # ✅ 여기서 유효성 검사
        VALID_MOODS = {"기쁨", "슬픔", "분노", "불안", "사랑", "중립"}
        VALID_DETAILED = {
            "희열", "만족", "감사", "설렘",
            "외로움", "상실감", "후회",
            "짜증", "분개", "억울함",
            "두려움", "긴장", "초조",
            "로맨스", "우정", "존경",
            "해당 없음",
        }

        if emotion_data["mood"] not in VALID_MOODS or emotion_data["detailed_mood"] not in VALID_DETAILED:
            raise ValueError(f"❌ 잘못된 감정 결과: {emotion_data}")

        # 저장
        letter.mood = emotion_data["mood"]
        letter.detailed_mood = emotion_data["detailed_mood"]
        letter.analyzed_at = now()
        letter.save(update_fields=["mood", "detailed_mood", "analyzed_at"])

        return emotion_data

    except Exception as e:
        print(f"❌ 감정 분석 실패: {e}")
        return None
