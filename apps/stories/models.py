from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid
from datetime import timedelta


def story_expiry():
    return timezone.now() + timedelta(hours=24)


class Story(models.Model):
    MEDIA_TYPES = [('image', 'Image'), ('video', 'Video')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='stories')
    media_url = models.URLField()
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES, default='image')
    thumbnail_url = models.URLField(blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    text_color = models.CharField(max_length=20, default='#FFFFFF')
    text_position_x = models.FloatField(default=0.5)
    text_position_y = models.FloatField(default=0.5)
    background_color = models.CharField(max_length=20, blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    duration = models.IntegerField(default=5)  # seconds
    expires_at = models.DateTimeField(default=story_expiry)
    is_highlight = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'stories'
        ordering = ['-created_at']

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    @property
    def views_count(self):
        return self.views.count()


class StoryView(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='views')
    viewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='story_views')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'story_views'
        unique_together = ('story', 'viewer')


class StoryReaction(models.Model):
    REACTIONS = [('❤️','heart'),('😂','laugh'),('😮','wow'),('😢','sad'),('😡','angry'),('👏','clap')]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='story_reactions')
    reaction = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'story_reactions'
        unique_together = ('story', 'user')


class StoryHighlight(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='highlights')
    title = models.CharField(max_length=15)
    cover_url = models.URLField(blank=True, null=True)
    stories = models.ManyToManyField(Story, related_name='highlights', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'story_highlights'
        ordering = ['-created_at']
