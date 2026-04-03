from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Like
from apps.posts.models import Post
from apps.reels.models import Reel
from apps.comments.models import Comment
from apps.notifications.utils import create_notification
from apps.users.serializers import UserMiniSerializer


class LikePostView(APIView):
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        if not created:
            return Response({'error': 'Already liked.'}, status=status.HTTP_400_BAD_REQUEST)
        if post.user != request.user:
            create_notification(sender=request.user, recipient=post.user,
                                notification_type='like_post', post=post)
        return Response({'liked': True, 'likes_count': post.likes_count}, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        Like.objects.filter(user=request.user, post=post).delete()
        return Response({'liked': False, 'likes_count': post.likes_count})


class LikeReelView(APIView):
    def post(self, request, pk):
        reel = get_object_or_404(Reel, pk=pk)
        like, created = Like.objects.get_or_create(user=request.user, reel=reel)
        if not created:
            return Response({'error': 'Already liked.'}, status=status.HTTP_400_BAD_REQUEST)
        if reel.user != request.user:
            create_notification(sender=request.user, recipient=reel.user,
                                notification_type='like_reel', reel=reel)
        return Response({'liked': True, 'likes_count': reel.likes_count}, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        reel = get_object_or_404(Reel, pk=pk)
        Like.objects.filter(user=request.user, reel=reel).delete()
        return Response({'liked': False, 'likes_count': reel.likes_count})


class LikeCommentView(APIView):
    def post(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        like, created = Like.objects.get_or_create(user=request.user, comment=comment)
        if not created:
            return Response({'error': 'Already liked.'}, status=status.HTTP_400_BAD_REQUEST)
        if comment.user != request.user:
            create_notification(sender=request.user, recipient=comment.user,
                                notification_type='like_comment', comment=comment)
        return Response({'liked': True, 'likes_count': comment.likes_count}, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        Like.objects.filter(user=request.user, comment=comment).delete()
        return Response({'liked': False, 'likes_count': comment.likes_count})


class PostLikersView(APIView):
    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        likers = [like.user for like in Like.objects.filter(post=post).select_related('user')]
        return Response(UserMiniSerializer(likers, many=True, context={'request': request}).data)


class ReelLikersView(APIView):
    def get(self, request, pk):
        reel = get_object_or_404(Reel, pk=pk)
        likers = [like.user for like in Like.objects.filter(reel=reel).select_related('user')]
        return Response(UserMiniSerializer(likers, many=True, context={'request': request}).data)
