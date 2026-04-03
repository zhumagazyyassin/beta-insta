from .models import Notification


def create_notification(sender, recipient, notification_type, post=None,
                         reel=None, comment=None, story=None):
    if sender == recipient:
        return None
    return Notification.objects.create(
        sender=sender,
        recipient=recipient,
        notification_type=notification_type,
        post=post,
        reel=reel,
        comment=comment,
        story=story
    )
