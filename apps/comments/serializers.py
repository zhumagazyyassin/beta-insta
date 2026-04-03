from rest_framework import serializers
from .models import Comment
from apps.users.serializers import UserMiniSerializer
from apps.likes.models import Like


class CommentSerializer(serializers.ModelSerializer):
    user = UserMiniSerializer(read_only=True)
    likes_count = serializers.ReadOnlyField()
    replies_count = serializers.ReadOnlyField()
    is_liked = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            'id', 'user', 'text', 'likes_count', 'replies_count',
            'is_liked', 'replies', 'parent', 'created_at', 'updated_at'
        ]

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Like.objects.filter(user=request.user, comment=obj).exists()
        return False

    def get_replies(self, obj):
        if obj.parent is None:  # Only top-level comments show replies
            replies = obj.replies.all()[:3]
            return CommentSerializer(replies, many=True, context=self.context).data
        return []


class CreateCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['text', 'parent']
