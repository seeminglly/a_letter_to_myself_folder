import pytest
import requests_mock
from unittest.mock import patch, Mock
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
@patch("openai.ChatCompletion.create")
def test_reanalyze_all_emotions_with_mocked_letters(mock_chat):
    # ✅ GPT 응답 mock (JSON 문자열)
    mock_message = Mock()
    mock_message.content = '{"mood": "기쁨", "detailed_mood": "감사"}'

    mock_choice = Mock()
    mock_choice.message = mock_message

    mock_response = Mock()
    mock_response.choices = [mock_choice]
    mock_chat.return_value = mock_response

    # ✅ 테스트 유저 생성 및 인증
    user = User.objects.create_user(username="testuser", password="password")
    client = APIClient()
    client.force_authenticate(user=user)

    # ✅ letter-service 응답 mock
    with requests_mock.Mocker() as mock:
        mock.get(
            requests_mock.ANY,
            json=[
                {"id": 1, "content": "기분이 우울했다."},
                {"id": 2, "content": "행복한 하루였다."}
            ],
            status_code=200
        )

        response = client.post("/emotions/analyze/")

    # ✅ 디버그 출력
    print("📦 상태 코드:", response.status_code)
    print("📦 응답 데이터:", response.data)

    # ✅ 검증
    assert response.status_code == 200
    assert response.data["status"] == "success"
    assert response.data["published_count"] == 2

