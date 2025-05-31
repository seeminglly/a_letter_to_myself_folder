from django.apps import AppConfig

class EmotionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    # name = 'emotions' -> 모놀리식으로 실행시킬 때 사용하는 경로
    name = 'emotions'
