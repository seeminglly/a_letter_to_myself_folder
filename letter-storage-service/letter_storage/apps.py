from django.apps import AppConfig


class LettersStorageConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField' # Django 3.2+ 기본값
    name = 'letter_storage' # 이 앱의 파이썬 경로. Django가 앱을 찾을 때 사용