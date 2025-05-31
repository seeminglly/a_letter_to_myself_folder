import requests
from django.conf import settings

USER_SERVICE_URL = "http://localhost:8000/profiles"

def create_user_in_user_service(username, email):
    response = requests.post(f"{USER_SERVICE_URL}/internal/users/", json={
        "username": username,
        "email": email,
    })
    print("User service response:", response.status_code, response.text)
    if response.status_code != 201:
        raise Exception("Failed to create user in user service")
    return response.json()["user_id"]

def get_user_by_email(email):
    raise NotImplementedError
