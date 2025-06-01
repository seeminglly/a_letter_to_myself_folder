import requests

AUTH_SERVICE_URL = "http://localhost:8001/auth"

def verify_access_token(token):
    try:
        # print(f"Verifying token: {token}") 토큰 확인
        response = requests.post(f"{AUTH_SERVICE_URL}/internal/verify/", json={"token": token})
        if response.status_code == 200:
            return response.json()['user_id']
        else:
            # 응답 내용을 로깅 또는 상세 반환
            try:
                return_detail = response.json().get('detail', response.text)
            except Exception:
                return_detail = response.text
            raise Exception(f"Token verification failed: {return_detail}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Auth service connection failed: {str(e)}")
