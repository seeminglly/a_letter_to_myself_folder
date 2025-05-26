from rest_framework import serializers
from .models import UserProfile

class UserCreateSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()

    def create(self, validated_data):
        from accounts.models import User
        user = User.objects.get(username=validated_data['username'])
        profile = UserProfile.objects.create(user=user)
        return profile

    def to_representation(self, instance):
        return {
            "user_id": instance.user.id,
        }


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'email', 'name', 'bio']


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['name', 'bio']
