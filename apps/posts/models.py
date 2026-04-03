from django.db import models
from django.conf import settings
import uuid


class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    caption = models.TextField(max_length=2200, blank=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    is_archived = models.BooleanField(default=False)
    disable_comments = models.BooleanField(default=False)
    hide_like_count = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'posts'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.id}"

    @property
    def likes_count(self):
        return self.likes.count()

    @property
    def comments_count(self):
        return self.comments.count()


class PostMedia(models.Model):
    MEDIA_TYPES = [('image', 'Image'), ('video', 'Video')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='media')
    url = models.URLField()
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES, default='image')
    thumbnail_url = models.URLField(blank=True, null=True)
    width = models.IntegerField(default=0)
    height = models.IntegerField(default=0)
    order = models.IntegerField(default=0)

    class Meta:
        db_table = 'post_media'
        ordering = ['order']


class PostTag(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='tags')
    tagged_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tagged_posts')
    x_position = models.FloatField(default=0)
    y_position = models.FloatField(default=0)

    class Meta:
        db_table = 'post_tags'
        unique_together = ('post', 'tagged_user')


class Hashtag(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    posts = models.ManyToManyField(Post, related_name='hashtags', blank=True)
    post_count = models.IntegerField(default=0)

    class Meta:
        db_table = 'hashtags'

    def __str__(self):
        return f"#{self.name}"


class SavedPost(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_posts')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='saves')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'saved_posts'
        unique_together = ('user', 'post')
        ordering = ['-created_at']


class Collection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='collections')
    name = models.CharField(max_length=100)
    cover_image = models.URLField(blank=True, null=True)
    posts = models.ManyToManyField(Post, related_name='collections', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'collections'
        unique_together = ('user', 'name')
