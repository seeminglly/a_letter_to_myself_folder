import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock

User = get_user_model()

@patch("openai.ChatCompletion.create")
@pytest.mark.django_db
def test_recommendation_view_authenticated(mock_openai):
    # mock된 응답 구조를 실제 기대하는 형태로 구성
    mock_response = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = "### 음악 추천\n노래1 - 팝\n노래2 - 발라드\n노래3 - 힙합"
    mock_response.choices = [mock_choice]
    mock_openai.return_value = mock_response

    user = User.objects.create_user(username="testuser", password="testpass")
    client = APIClient()
    client.login(username="testuser", password="testpass")

    response = client.post("/recommend/emotion-based/", {"most_frequent_mood": "기쁨"}, format="json")

    assert response.status_code == 200
    assert "recommendations" in response.data