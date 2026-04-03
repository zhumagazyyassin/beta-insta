from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.db.models import Q
from apps.users.serializers import UserMiniSerializer
from apps.posts.models import Post, Hashtag
from apps.posts.serializers import PostSerializer, HashtagSerializer

User = get_user_model()


class SearchView(APIView):
    def get(self, request):
        query = request.query_params.get('q', '').strip()
        search_type = request.query_params.get('type', 'all')  # all, users, posts, hashtags

        if not query:
            return Response({'users': [], 'posts': [], 'hashtags': []})

        result = {}

        if search_type in ['all', 'users']:
            users = User.objects.filter(
                Q(username__icontains=query) | Q(full_name__icontains=query)
            ).exclude(id=request.user.id)[:20]
            result['users'] = UserMiniSerializer(users, many=True, context={'request': request}).data

        if search_type in ['all', 'hashtags']:
            hashtags = Hashtag.objects.filter(name__icontains=query.lstrip('#'))[:10]
            result['hashtags'] = HashtagSerializer(hashtags, many=True).data

        if search_type in ['all', 'posts']:
            posts = Post.objects.filter(
                Q(caption__icontains=query) | Q(location__icontains=query),
                is_archived=False
            ).select_related('user').prefetch_related('media')[:20]
            result['posts'] = PostSerializer(posts, many=True, context={'request': request}).data

        return Response(result)


class SearchUsersView(APIView):
    def get(self, request):
        query = request.query_params.get('q', '').strip()
        if not query:
            return Response([])
        users = User.objects.filter(
            Q(username__icontains=query) | Q(full_name__icontains=query)
        ).exclude(id=request.user.id)[:20]
        return Response(UserMiniSerializer(users, many=True, context={'request': request}).data)


class TrendingHashtagsView(APIView):
    def get(self, request):
        hashtags = Hashtag.objects.order_by('-post_count')[:20]
        return Response(HashtagSerializer(hashtags, many=True).data)
