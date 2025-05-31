from rest_framework import serializers
from .models import UserProfile

class UserCreateSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()

    def create(self, validated_data):
        return UserProfile.objects.create(user_id=validated_data["user_id"])

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            'id', 'user_id',
            'profile_picture', 'nickname', 'bio',
            'birthday', 'blog_url',
        ]

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'nickname', 'bio', 
                  'birthday', 'blog_url']
