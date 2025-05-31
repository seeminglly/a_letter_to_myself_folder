import requests

USER_SERVICE_URL = "http://localhost:8002/user" # 개발환경 기준

def create_user_in_user_service(user_id, username, email):
    payload = {
        "user_id": user_id,
        "username": username,
        "email": email,
    }
    try:
        response = requests.post(f'{USER_SERVICE_URL}/internal/users/', json=payload)
        if response.status_code == 201:
            return response.json()  # 예: {"user_id": 123}
        else:
            # 실패시 상세 메시지 포함해서 예외 발생
            try:
                detail = response.json().get("detail", response.text)
            except Exception:
                detail = response.text
            raise Exception(f"User service error: {detail}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"User service connection failed: {str(e)}")