from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .models import Follow, BlockedUser
from apps.notifications.utils import create_notification
from apps.users.serializers import UserMiniSerializer

User = get_user_model()


class FollowView(APIView):
    def post(self, request, username):
        target = get_object_or_404(User, username=username)
        if target == request.user:
            return Response({'error': 'Cannot follow yourself.'}, status=status.HTTP_400_BAD_REQUEST)
        if BlockedUser.objects.filter(blocker=target, blocked=request.user).exists():
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        follow, created = Follow.objects.get_or_create(
            follower=request.user,
            following=target,
            defaults={'status': 'pending' if target.is_private else 'accepted'}
        )
        if not created:
            return Response({'error': 'Already following or request pending.'}, status=status.HTTP_400_BAD_REQUEST)
        notif_type = 'follow_request' if target.is_private else 'follow'
        create_notification(sender=request.user, recipient=target, notification_type=notif_type)
        return Response({
            'status': follow.status,
            'message': 'Follow request sent.' if target.is_private else 'Now following.'
        }, status=status.HTTP_201_CREATED)

    def delete(self, request, username):
        target = get_object_or_404(User, username=username)
        Follow.objects.filter(follower=request.user, following=target).delete()
        return Response({'message': 'Unfollowed.'})


class AcceptFollowRequestView(APIView):
    def post(self, request, username):
        follower = get_object_or_404(User, username=username)
        follow = get_object_or_404(Follow, follower=follower, following=request.user, status='pending')
        follow.status = 'accepted'
        follow.save()
        create_notification(sender=request.user, recipient=follower, notification_type='follow_accept')
        return Response({'message': 'Follow request accepted.'})

    def delete(self, request, username):
        follower = get_object_or_404(User, username=username)
        Follow.objects.filter(follower=follower, following=request.user, status='pending').delete()
        return Response({'message': 'Follow request declined.'})


class RemoveFollowerView(APIView):
    def delete(self, request, username):
        follower = get_object_or_404(User, username=username)
        Follow.objects.filter(follower=follower, following=request.user).delete()
        return Response({'message': 'Follower removed.'})


class PendingRequestsView(APIView):
    def get(self, request):
        pending = Follow.objects.filter(following=request.user, status='pending').select_related('follower')
        users = [f.follower for f in pending]
        return Response(UserMiniSerializer(users, many=True, context={'request': request}).data)


class BlockView(APIView):
    def post(self, request, username):
        target = get_object_or_404(User, username=username)
        if target == request.user:
            return Response({'error': 'Cannot block yourself.'}, status=status.HTTP_400_BAD_REQUEST)
        BlockedUser.objects.get_or_create(blocker=request.user, blocked=target)
        # Remove any follow relationships
        Follow.objects.filter(follower=request.user, following=target).delete()
        Follow.objects.filter(follower=target, following=request.user).delete()
        return Response({'message': f'{target.username} blocked.'}, status=status.HTTP_201_CREATED)

    def delete(self, request, username):
        target = get_object_or_404(User, username=username)
        BlockedUser.objects.filter(blocker=request.user, blocked=target).delete()
        return Response({'message': f'{target.username} unblocked.'})


class BlockedUsersView(APIView):
    def get(self, request):
        blocked = BlockedUser.objects.filter(blocker=request.user).select_related('blocked')
        users = [b.blocked for b in blocked]
        return Response(UserMiniSerializer(users, many=True, context={'request': request}).data)
