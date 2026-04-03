from rest_framework import serializers
from .models import Like
from apps.users.serializers import UserMiniSerializer

class LikeSerializer(serializers.ModelSerializer):
    user = UserMiniSerializer(read_only=True)
    class Meta:
        model = Like
        fields = ['id', 'user', 'created_at']
