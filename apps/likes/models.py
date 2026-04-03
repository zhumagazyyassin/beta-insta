from django.db import models
from django.conf import settings
import uuid


class Like(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey('posts.Post', on_delete=models.CASCADE, related_name='likes', null=True, blank=True)
    reel = models.ForeignKey('reels.Reel', on_delete=models.CASCADE, related_name='likes', null=True, blank=True)
    comment = models.ForeignKey('comments.Comment', on_delete=models.CASCADE, related_name='likes', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'likes'
        unique_together = [
            ('user', 'post'),
            ('user', 'reel'),
            ('user', 'comment'),
        ]
        ordering = ['-created_at']

    def __str__(self):
        target = self.post or self.reel or self.comment
        return f"{self.user.username} liked {target}"
