from django.apps import AppConfig

class EmotionBasedConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    #마이크로서비스로 실행할 때 사용하는 경로
    #name = 'recommendation.emotion_based'  # 이것도 settings.py에 등록
    
    #모놀리식으로 실행시킬 때 사용하는 경로
    name = 'emotion_recommendation.recommendation.emotion_based'  # ✅ 진짜 모듈 경로

