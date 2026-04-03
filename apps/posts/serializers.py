from rest_framework import serializers
from .models import Post, PostMedia, PostTag, Hashtag, SavedPost, Collection
from apps.users.serializers import UserMiniSerializer
from apps.likes.models import Like


class PostMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostMedia
        fields = ['id', 'url', 'media_type', 'thumbnail_url', 'width', 'height', 'order']


class PostTagSerializer(serializers.ModelSerializer):
    tagged_user = UserMiniSerializer(read_only=True)
    tagged_user_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = PostTag
        fields = ['id', 'tagged_user', 'tagged_user_id', 'x_position', 'y_position']


class HashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hashtag
        fields = ['id', 'name', 'post_count']


class PostSerializer(serializers.ModelSerializer):
    user = UserMiniSerializer(read_only=True)
    media = PostMediaSerializer(many=True, read_only=True)
    tags = PostTagSerializer(many=True, read_only=True)
    hashtags = HashtagSerializer(many=True, read_only=True)
    likes_count = serializers.ReadOnlyField()
    comments_count = serializers.ReadOnlyField()
    is_liked = serializers.SerializerMethodField()
    is_saved = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'user', 'caption', 'location', 'media', 'tags', 'hashtags',
            'likes_count', 'comments_count', 'is_liked', 'is_saved',
            'disable_comments', 'hide_like_count', 'created_at', 'updated_at'
        ]

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Like.objects.filter(user=request.user, post=obj).exists()
        return False

    def get_is_saved(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.saves.filter(user=request.user).exists()
        return False


class CreatePostSerializer(serializers.ModelSerializer):
    media = PostMediaSerializer(many=True, required=True)

    class Meta:
        model = Post
        fields = ['caption', 'location', 'media', 'disable_comments', 'hide_like_count']

    def create(self, validated_data):
        media_data = validated_data.pop('media')
        post = Post.objects.create(**validated_data)
        for idx, m in enumerate(media_data):
            PostMedia.objects.create(post=post, order=idx, **m)
        return post


class SavedPostSerializer(serializers.ModelSerializer):
    post = PostSerializer(read_only=True)

    class Meta:
        model = SavedPost
        fields = ['id', 'post', 'created_at']


class CollectionSerializer(serializers.ModelSerializer):
    posts_count = serializers.SerializerMethodField()

    class Meta:
        model = Collection
        fields = ['id', 'name', 'cover_image', 'posts_count', 'created_at']

    def get_posts_count(self, obj):
        return obj.posts.count()
