from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .models import Post, PostMedia, PostTag, Hashtag, SavedPost, Collection
from .serializers import (
    PostSerializer, CreatePostSerializer,
    SavedPostSerializer, CollectionSerializer, HashtagSerializer
)
from apps.follows.models import Follow
from apps.notifications.utils import create_notification
import re

User = get_user_model()


def extract_hashtags(caption):
    return re.findall(r'#(\w+)', caption)


class FeedView(generics.ListAPIView):
    serializer_class = PostSerializer

    def get_queryset(self):
        following_ids = Follow.objects.filter(
            follower=self.request.user, status='accepted'
        ).values_list('following_id', flat=True)
        return Post.objects.filter(
            user_id__in=list(following_ids) + [self.request.user.id],
            is_archived=False
        ).prefetch_related('media', 'tags', 'hashtags', 'likes').select_related('user')

    def get_serializer_context(self):
        return {'request': self.request}


class ExploreFeedView(generics.ListAPIView):
    serializer_class = PostSerializer

    def get_queryset(self):
        following_ids = Follow.objects.filter(
            follower=self.request.user, status='accepted'
        ).values_list('following_id', flat=True)
        return Post.objects.exclude(
            user_id__in=list(following_ids) + [self.request.user.id]
        ).filter(is_archived=False).order_by('-created_at')

    def get_serializer_context(self):
        return {'request': self.request}


class PostListCreateView(APIView):
    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        posts = Post.objects.filter(user=user, is_archived=False).prefetch_related('media')
        serializer = PostSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        serializer = CreatePostSerializer(data=request.data)
        if serializer.is_valid():
            post = serializer.save(user=request.user)
            # Handle hashtags
            tags = extract_hashtags(post.caption)
            for tag_name in tags:
                hashtag, _ = Hashtag.objects.get_or_create(name=tag_name.lower())
                hashtag.posts.add(post)
                hashtag.post_count = hashtag.posts.count()
                hashtag.save()
            return Response(PostSerializer(post, context={'request': request}).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDetailView(APIView):
    def get_object(self, pk):
        return get_object_or_404(Post, pk=pk)

    def get(self, request, pk):
        post = self.get_object(pk)
        return Response(PostSerializer(post, context={'request': request}).data)

    def put(self, request, pk):
        post = self.get_object(pk)
        if post.user != request.user:
            return Response({'error': 'Not authorized.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = CreatePostSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(PostSerializer(post, context={'request': request}).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        return self.put(request, pk)

    def delete(self, request, pk):
        post = self.get_object(pk)
        if post.user != request.user:
            return Response({'error': 'Not authorized.'}, status=status.HTTP_403_FORBIDDEN)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SavedPostsView(APIView):
    def get(self, request):
        saved = SavedPost.objects.filter(user=request.user).select_related('post')
        serializer = SavedPostSerializer(saved, many=True, context={'request': request})
        return Response(serializer.data)


class SavePostView(APIView):
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        saved, created = SavedPost.objects.get_or_create(user=request.user, post=post)
        if not created:
            return Response({'error': 'Already saved.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'Post saved.'}, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        SavedPost.objects.filter(user=request.user, post=post).delete()
        return Response({'message': 'Post unsaved.'}, status=status.HTTP_204_NO_CONTENT)


class CollectionListCreateView(APIView):
    def get(self, request):
        collections = Collection.objects.filter(user=request.user)
        return Response(CollectionSerializer(collections, many=True).data)

    def post(self, request):
        serializer = CollectionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CollectionDetailView(APIView):
    def get(self, request, pk):
        collection = get_object_or_404(Collection, pk=pk, user=request.user)
        posts = PostSerializer(collection.posts.all(), many=True, context={'request': request})
        return Response({'collection': CollectionSerializer(collection).data, 'posts': posts.data})

    def put(self, request, pk):
        collection = get_object_or_404(Collection, pk=pk, user=request.user)
        serializer = CollectionSerializer(collection, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        collection = get_object_or_404(Collection, pk=pk, user=request.user)
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AddToCollectionView(APIView):
    def post(self, request, pk, post_id):
        collection = get_object_or_404(Collection, pk=pk, user=request.user)
        post = get_object_or_404(Post, pk=post_id)
        collection.posts.add(post)
        return Response({'message': 'Post added to collection.'})

    def delete(self, request, pk, post_id):
        collection = get_object_or_404(Collection, pk=pk, user=request.user)
        post = get_object_or_404(Post, pk=post_id)
        collection.posts.remove(post)
        return Response({'message': 'Post removed from collection.'})


class HashtagPostsView(generics.ListAPIView):
    serializer_class = PostSerializer

    def get_queryset(self):
        name = self.kwargs['name'].lower()
        hashtag = get_object_or_404(Hashtag, name=name)
        return hashtag.posts.filter(is_archived=False).order_by('-created_at')

    def get_serializer_context(self):
        return {'request': self.request}


class ArchivedPostsView(generics.ListAPIView):
    serializer_class = PostSerializer

    def get_queryset(self):
        return Post.objects.filter(user=self.request.user, is_archived=True)

    def get_serializer_context(self):
        return {'request': self.request}


class ArchivePostView(APIView):
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk, user=request.user)
        post.is_archived = True
        post.save()
        return Response({'message': 'Post archived.'})

    def delete(self, request, pk):
        post = get_object_or_404(Post, pk=pk, user=request.user)
        post.is_archived = False
        post.save()
        return Response({'message': 'Post unarchived.'})
