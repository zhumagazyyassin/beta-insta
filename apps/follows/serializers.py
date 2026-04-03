from rest_framework import serializers
from .models import Follow
from apps.users.serializers import UserMiniSerializer

class FollowSerializer(serializers.ModelSerializer):
    follower = UserMiniSerializer(read_only=True)
    following = UserMiniSerializer(read_only=True)
    class Meta:
        model = Follow
        fields = ['id', 'follower', 'following', 'status', 'created_at']
