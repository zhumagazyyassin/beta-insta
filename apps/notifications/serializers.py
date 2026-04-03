from rest_framework import serializers
from .models import Notification
from apps.users.serializers import UserMiniSerializer


class NotificationSerializer(serializers.ModelSerializer):
    sender = UserMiniSerializer(read_only=True)
    post_id = serializers.UUIDField(source='post.id', read_only=True, allow_null=True)
    reel_id = serializers.UUIDField(source='reel.id', read_only=True, allow_null=True)
    comment_id = serializers.UUIDField(source='comment.id', read_only=True, allow_null=True)
    story_id = serializers.UUIDField(source='story.id', read_only=True, allow_null=True)
    post_thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            'id', 'sender', 'notification_type', 'post_id', 'reel_id',
            'comment_id', 'story_id', 'post_thumbnail', 'is_read', 'created_at'
        ]

    def get_post_thumbnail(self, obj):
        if obj.post:
            first_media = obj.post.media.first()
            return first_media.url if first_media else None
        return None
