from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Comment
from .serializers import CommentSerializer, CreateCommentSerializer
from apps.posts.models import Post
from apps.reels.models import Reel
from apps.notifications.utils import create_notification


class PostCommentsView(APIView):
    def get(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        comments = Comment.objects.filter(post=post, parent=None).select_related('user')
        return Response(CommentSerializer(comments, many=True, context={'request': request}).data)

    def post(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        if post.disable_comments:
            return Response({'error': 'Comments are disabled.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = CreateCommentSerializer(data=request.data)
        if serializer.is_valid():
            comment = serializer.save(user=request.user, post=post)
            if post.user != request.user:
                notif_type = 'reply' if comment.parent else 'comment'
                recipient = comment.parent.user if comment.parent else post.user
                create_notification(sender=request.user, recipient=recipient,
                                    notification_type=notif_type, post=post, comment=comment)
            return Response(CommentSerializer(comment, context={'request': request}).data,
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReelCommentsView(APIView):
    def get(self, request, reel_id):
        reel = get_object_or_404(Reel, pk=reel_id)
        comments = Comment.objects.filter(reel=reel, parent=None).select_related('user')
        return Response(CommentSerializer(comments, many=True, context={'request': request}).data)

    def post(self, request, reel_id):
        reel = get_object_or_404(Reel, pk=reel_id)
        serializer = CreateCommentSerializer(data=request.data)
        if serializer.is_valid():
            comment = serializer.save(user=request.user, reel=reel)
            return Response(CommentSerializer(comment, context={'request': request}).data,
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentDetailView(APIView):
    def get(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        return Response(CommentSerializer(comment, context={'request': request}).data)

    def put(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk, user=request.user)
        serializer = CreateCommentSerializer(comment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(CommentSerializer(comment, context={'request': request}).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        return self.put(request, pk)

    def delete(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        post_owner = comment.post.user if comment.post else None
        reel_owner = comment.reel.user if comment.reel else None
        if comment.user != request.user and request.user not in [post_owner, reel_owner]:
            return Response({'error': 'Not authorized.'}, status=status.HTTP_403_FORBIDDEN)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentRepliesView(generics.ListAPIView):
    serializer_class = CommentSerializer

    def get_queryset(self):
        comment = get_object_or_404(Comment, pk=self.kwargs['pk'])
        return comment.replies.all()

    def get_serializer_context(self):
        return {'request': self.request}
