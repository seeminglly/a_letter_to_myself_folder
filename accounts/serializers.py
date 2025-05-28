from rest_framework import serializers

class TokenRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()

class TokenVerifySerializer(serializers.Serializer):
    token = serializers.CharField()