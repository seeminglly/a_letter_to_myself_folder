from django.apps import AppConfig

class FeedbackConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    #이건 마이크로서비스의 경로
    #name = 'recommendation.feedback'  # ← 반드시 정확히 써야 함
    
    #모놀리식 경로
    name = 'emotion_recommendation.recommendation.feedback'  # ✅ 전체 경로로 고치기
