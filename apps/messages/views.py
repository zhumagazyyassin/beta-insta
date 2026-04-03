from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import DirectChat, Message, MessageReaction, MessageReadReceipt
from .serializers import DirectChatSerializer, MessageSerializer, CreateMessageSerializer, MessageReactionSerializer

User = get_user_model()


class ChatListView(APIView):
    def get(self, request):
        chats = DirectChat.objects.filter(participants=request.user).order_by('-updated_at')
        return Response(DirectChatSerializer(chats, many=True, context={'request': request}).data)

    def post(self, request):
        """Start a new DM with a user or create group chat"""
        participant_ids = request.data.get('participant_ids', [])
        is_group = request.data.get('is_group', False)
        if not participant_ids:
            return Response({'error': 'participant_ids required.'}, status=status.HTTP_400_BAD_REQUEST)
        participants = User.objects.filter(id__in=participant_ids)
        if not is_group and len(participants) == 1:
            # Check for existing DM
            target = participants.first()
            existing = DirectChat.objects.filter(
                participants=request.user, is_group=False
            ).filter(participants=target)
            if existing.exists():
                return Response(DirectChatSerializer(existing.first(), context={'request': request}).data)
        chat = DirectChat.objects.create(
            is_group=is_group,
            group_name=request.data.get('group_name'),
            created_by=request.user
        )
        chat.participants.add(request.user, *participants)
        return Response(DirectChatSerializer(chat, context={'request': request}).data,
                        status=status.HTTP_201_CREATED)


class ChatDetailView(APIView):
    def get(self, request, pk):
        chat = get_object_or_404(DirectChat, pk=pk, participants=request.user)
        return Response(DirectChatSerializer(chat, context={'request': request}).data)

    def put(self, request, pk):
        chat = get_object_or_404(DirectChat, pk=pk, participants=request.user)
        if not chat.is_group:
            return Response({'error': 'Cannot edit DM chats.'}, status=status.HTTP_400_BAD_REQUEST)
        if 'group_name' in request.data:
            chat.group_name = request.data['group_name']
        if 'group_avatar' in request.data:
            chat.group_avatar = request.data['group_avatar']
        chat.save()
        return Response(DirectChatSerializer(chat, context={'request': request}).data)

    def delete(self, request, pk):
        chat = get_object_or_404(DirectChat, pk=pk, participants=request.user)
        chat.participants.remove(request.user)
        if chat.participants.count() == 0:
            chat.delete()
        return Response({'message': 'Left chat.'})


class MessageListView(APIView):
    def get(self, request, chat_id):
        chat = get_object_or_404(DirectChat, pk=chat_id, participants=request.user)
        messages = chat.messages.filter(is_deleted=False).order_by('created_at')
        # Auto mark as read
        for msg in messages.exclude(sender=request.user):
            MessageReadReceipt.objects.get_or_create(message=msg, user=request.user)
        return Response(MessageSerializer(messages, many=True, context={'request': request}).data)

    def post(self, request, chat_id):
        chat = get_object_or_404(DirectChat, pk=chat_id, participants=request.user)
        serializer = CreateMessageSerializer(data=request.data)
        if serializer.is_valid():
            message = serializer.save(sender=request.user, chat=chat)
            chat.save()  # Update updated_at
            return Response(MessageSerializer(message, context={'request': request}).data,
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MessageDetailView(APIView):
    def delete(self, request, chat_id, pk):
        chat = get_object_or_404(DirectChat, pk=chat_id, participants=request.user)
        message = get_object_or_404(Message, pk=pk, chat=chat, sender=request.user)
        message.is_deleted = True
        message.text = None
        message.media_url = None
        message.save()
        return Response({'message': 'Message deleted.'})


class MessageReactionView(APIView):
    def post(self, request, chat_id, pk):
        chat = get_object_or_404(DirectChat, pk=chat_id, participants=request.user)
        message = get_object_or_404(Message, pk=pk, chat=chat)
        emoji = request.data.get('emoji')
        if not emoji:
            return Response({'error': 'Emoji required.'}, status=status.HTTP_400_BAD_REQUEST)
        reaction, created = MessageReaction.objects.update_or_create(
            message=message, user=request.user, defaults={'emoji': emoji}
        )
        return Response(MessageReactionSerializer(reaction).data)

    def delete(self, request, chat_id, pk):
        chat = get_object_or_404(DirectChat, pk=chat_id, participants=request.user)
        message = get_object_or_404(Message, pk=pk, chat=chat)
        MessageReaction.objects.filter(message=message, user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
