from rest_framework import serializers
from .models import DirectChat, Message, MessageReaction, MessageReadReceipt
from apps.users.serializers import UserMiniSerializer


class MessageReactionSerializer(serializers.ModelSerializer):
    user = UserMiniSerializer(read_only=True)

    class Meta:
        model = MessageReaction
        fields = ['id', 'user', 'emoji', 'created_at']


class MessageSerializer(serializers.ModelSerializer):
    sender = UserMiniSerializer(read_only=True)
    reactions = MessageReactionSerializer(many=True, read_only=True)
    reply_to_text = serializers.SerializerMethodField()
    is_read = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            'id', 'sender', 'message_type', 'text', 'media_url',
            'shared_post', 'shared_reel', 'shared_story', 'reply_to',
            'reply_to_text', 'reactions', 'is_read', 'is_deleted', 'created_at'
        ]

    def get_reply_to_text(self, obj):
        if obj.reply_to:
            return obj.reply_to.text or '[media]'
        return None

    def get_is_read(self, obj):
        request = self.context.get('request')
        if request:
            return MessageReadReceipt.objects.filter(message=obj, user=request.user).exists()
        return False


class CreateMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['message_type', 'text', 'media_url', 'shared_post', 'shared_reel', 'shared_story', 'reply_to']


class DirectChatSerializer(serializers.ModelSerializer):
    participants = UserMiniSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = DirectChat
        fields = ['id', 'participants', 'is_group', 'group_name', 'group_avatar',
                  'last_message', 'unread_count', 'created_at', 'updated_at']

    def get_last_message(self, obj):
        last = obj.messages.filter(is_deleted=False).last()
        if last:
            return {'text': last.text, 'sender': last.sender.username, 'created_at': last.created_at}
        return None

    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request:
            read_ids = MessageReadReceipt.objects.filter(
                user=request.user, message__chat=obj
            ).values_list('message_id', flat=True)
            return obj.messages.filter(is_deleted=False).exclude(
                id__in=read_ids
            ).exclude(sender=request.user).count()
        return 0
