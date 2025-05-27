import jwt
from datetime import datetime, timedelta
from django.conf import settings
from jwt import ExpiredSignatureError, InvalidTokenError

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = 'HS256'
ACCESS_TOKEN_LIFETIME = timedelta(minutes=15)
REFRESH_TOKEN_LIFETIME = timedelta(days=7)

def create_access_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + ACCESS_TOKEN_LIFETIME,
        'type': 'access'
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + REFRESH_TOKEN_LIFETIME,
        'type': 'refresh'
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token, token_type='access'):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get('type') != token_type:
            raise InvalidTokenError('Invalid token type')
        return payload['user_id']
    except ExpiredSignatureError:
        raise ExpiredSignatureError('Token expired')
    except InvalidTokenError:
        raise InvalidTokenError('Invalid token')
