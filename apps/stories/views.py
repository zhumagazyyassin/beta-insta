from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Story, StoryView, StoryReaction, StoryHighlight
from .serializers import (
    StorySerializer, CreateStorySerializer,
    StoryViewSerializer, StoryReactionSerializer, StoryHighlightSerializer
)
from apps.follows.models import Follow

User = get_user_model()


class StoryFeedView(APIView):
    """Get stories from followed users, grouped by user"""
    def get(self, request):
        following_ids = Follow.objects.filter(
            follower=request.user, status='accepted'
        ).values_list('following_id', flat=True)
        user_ids = list(following_ids) + [request.user.id]
        active_stories = Story.objects.filter(
            user_id__in=user_ids,
            expires_at__gt=timezone.now(),
            is_highlight=False
        ).select_related('user').order_by('user_id', '-created_at')
        # Group by user
        grouped = {}
        for story in active_stories:
            uid = str(story.user.id)
            if uid not in grouped:
                grouped[uid] = {'user': story.user, 'stories': []}
            grouped[uid]['stories'].append(story)
        result = []
        for uid, data in grouped.items():
            stories_serialized = StorySerializer(data['stories'], many=True, context={'request': request}).data
            from apps.users.serializers import UserMiniSerializer
            result.append({
                'user': UserMiniSerializer(data['user'], context={'request': request}).data,
                'stories': stories_serialized,
                'has_unseen': any(not s['is_viewed'] for s in stories_serialized)
            })
        return Response(result)


class StoryCreateView(APIView):
    def post(self, request):
        serializer = CreateStorySerializer(data=request.data)
        if serializer.is_valid():
            story = serializer.save(user=request.user)
            return Response(StorySerializer(story, context={'request': request}).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StoryDetailView(APIView):
    def get(self, request, pk):
        story = get_object_or_404(Story, pk=pk)
        # Auto-record view
        if request.user != story.user:
            StoryView.objects.get_or_create(story=story, viewer=request.user)
        return Response(StorySerializer(story, context={'request': request}).data)

    def delete(self, request, pk):
        story = get_object_or_404(Story, pk=pk, user=request.user)
        story.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class StoryViewersView(APIView):
    def get(self, request, pk):
        story = get_object_or_404(Story, pk=pk, user=request.user)
        views = StoryView.objects.filter(story=story).select_related('viewer')
        return Response(StoryViewSerializer(views, many=True).data)


class StoryReactionView(APIView):
    def post(self, request, pk):
        story = get_object_or_404(Story, pk=pk)
        reaction_emoji = request.data.get('reaction')
        if not reaction_emoji:
            return Response({'error': 'Reaction required.'}, status=status.HTTP_400_BAD_REQUEST)
        reaction, created = StoryReaction.objects.update_or_create(
            story=story, user=request.user,
            defaults={'reaction': reaction_emoji}
        )
        return Response(StoryReactionSerializer(reaction).data,
                        status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    def delete(self, request, pk):
        story = get_object_or_404(Story, pk=pk)
        StoryReaction.objects.filter(story=story, user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserStoriesView(APIView):
    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        stories = Story.objects.filter(
            user=user, expires_at__gt=timezone.now(), is_highlight=False
        ).order_by('created_at')
        return Response(StorySerializer(stories, many=True, context={'request': request}).data)


class HighlightListCreateView(APIView):
    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        highlights = StoryHighlight.objects.filter(user=user)
        return Response(StoryHighlightSerializer(highlights, many=True).data)

    def post(self, request):
        serializer = StoryHighlightSerializer(data=request.data)
        if serializer.is_valid():
            highlight = serializer.save(user=request.user)
            story_ids = request.data.get('story_ids', [])
            if story_ids:
                stories = Story.objects.filter(id__in=story_ids, user=request.user)
                highlight.stories.set(stories)
            return Response(StoryHighlightSerializer(highlight).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HighlightDetailView(APIView):
    def get(self, request, pk):
        highlight = get_object_or_404(StoryHighlight, pk=pk)
        return Response(StoryHighlightSerializer(highlight).data)

    def put(self, request, pk):
        highlight = get_object_or_404(StoryHighlight, pk=pk, user=request.user)
        serializer = StoryHighlightSerializer(highlight, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            if 'story_ids' in request.data:
                stories = Story.objects.filter(id__in=request.data['story_ids'], user=request.user)
                highlight.stories.set(stories)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        highlight = get_object_or_404(StoryHighlight, pk=pk, user=request.user)
        highlight.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
