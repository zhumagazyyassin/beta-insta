from django.db import models
from django.conf import settings
import uuid


class Reel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reels')
    video_url = models.URLField()
    thumbnail_url = models.URLField(blank=True, null=True)
    caption = models.TextField(max_length=2200, blank=True)
    audio_name = models.CharField(max_length=100, blank=True, null=True)
    audio_artist = models.CharField(max_length=100, blank=True, null=True)
    duration = models.IntegerField(default=0)  # seconds
    width = models.IntegerField(default=1080)
    height = models.IntegerField(default=1920)
    view_count = models.BigIntegerField(default=0)
    share_count = models.BigIntegerField(default=0)
    disable_comments = models.BooleanField(default=False)
    hide_like_count = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'reels'
        ordering = ['-created_at']

    def __str__(self):
        return f"Reel by {self.user.username}"

    @property
    def likes_count(self):
        return self.likes.count()

    @property
    def comments_count(self):
        return self.comments.count()
