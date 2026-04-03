from rest_framework import serializers
from .models import Story, StoryView, StoryReaction, StoryHighlight
from apps.users.serializers import UserMiniSerializer


class StorySerializer(serializers.ModelSerializer):
    user = UserMiniSerializer(read_only=True)
    views_count = serializers.ReadOnlyField()
    is_viewed = serializers.SerializerMethodField()
    is_expired = serializers.ReadOnlyField()

    class Meta:
        model = Story
        fields = [
            'id', 'user', 'media_url', 'media_type', 'thumbnail_url',
            'text', 'text_color', 'text_position_x', 'text_position_y',
            'background_color', 'link', 'duration', 'expires_at',
            'views_count', 'is_viewed', 'is_expired', 'created_at'
        ]

    def get_is_viewed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return StoryView.objects.filter(story=obj, viewer=request.user).exists()
        return False


class CreateStorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = [
            'media_url', 'media_type', 'thumbnail_url', 'text', 'text_color',
            'text_position_x', 'text_position_y', 'background_color', 'link', 'duration'
        ]


class StoryViewSerializer(serializers.ModelSerializer):
    viewer = UserMiniSerializer(read_only=True)

    class Meta:
        model = StoryView
        fields = ['id', 'viewer', 'created_at']


class StoryReactionSerializer(serializers.ModelSerializer):
    user = UserMiniSerializer(read_only=True)

    class Meta:
        model = StoryReaction
        fields = ['id', 'user', 'reaction', 'created_at']


class StoryHighlightSerializer(serializers.ModelSerializer):
    stories = StorySerializer(many=True, read_only=True)
    stories_count = serializers.SerializerMethodField()

    class Meta:
        model = StoryHighlight
        fields = ['id', 'title', 'cover_url', 'stories', 'stories_count', 'created_at']

    def get_stories_count(self, obj):
        return obj.stories.count()
