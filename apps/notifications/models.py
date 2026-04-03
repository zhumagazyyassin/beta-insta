from django.db import models
from django.conf import settings
import uuid


class Notification(models.Model):
    TYPES = [
        ('like_post', 'Liked your post'),
        ('like_reel', 'Liked your reel'),
        ('like_comment', 'Liked your comment'),
        ('comment', 'Commented on your post'),
        ('comment_reel', 'Commented on your reel'),
        ('reply', 'Replied to your comment'),
        ('follow', 'Started following you'),
        ('follow_request', 'Requested to follow you'),
        ('follow_accept', 'Accepted your follow request'),
        ('mention_post', 'Mentioned you in a post'),
        ('mention_comment', 'Mentioned you in a comment'),
        ('tag_post', 'Tagged you in a post'),
        ('story_reaction', 'Reacted to your story'),
        ('story_reply', 'Replied to your story'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_notifications')
    notification_type = models.CharField(max_length=20, choices=TYPES)
    post = models.ForeignKey('posts.Post', on_delete=models.SET_NULL, null=True, blank=True)
    reel = models.ForeignKey('reels.Reel', on_delete=models.SET_NULL, null=True, blank=True)
    comment = models.ForeignKey('comments.Comment', on_delete=models.SET_NULL, null=True, blank=True)
    story = models.ForeignKey('stories.Story', on_delete=models.SET_NULL, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.sender.username} -> {self.recipient.username}: {self.notification_type}"
