from rest_framework import serializers
from .models import Reel
from apps.users.serializers import UserMiniSerializer
from apps.likes.models import Like


class ReelSerializer(serializers.ModelSerializer):
    user = UserMiniSerializer(read_only=True)
    likes_count = serializers.ReadOnlyField()
    comments_count = serializers.ReadOnlyField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Reel
        fields = [
            'id', 'user', 'video_url', 'thumbnail_url', 'caption',
            'audio_name', 'audio_artist', 'duration', 'width', 'height',
            'view_count', 'share_count', 'likes_count', 'comments_count',
            'is_liked', 'disable_comments', 'hide_like_count', 'created_at'
        ]

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Like.objects.filter(user=request.user, reel=obj).exists()
        return False


class CreateReelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reel
        fields = ['video_url', 'thumbnail_url', 'caption', 'audio_name', 'audio_artist',
                  'duration', 'width', 'height', 'disable_comments', 'hide_like_count']
