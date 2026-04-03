from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .models import Reel
from .serializers import ReelSerializer, CreateReelSerializer
from apps.follows.models import Follow

User = get_user_model()


class ReelFeedView(generics.ListAPIView):
    serializer_class = ReelSerializer

    def get_queryset(self):
        return Reel.objects.filter(is_archived=False).order_by('-created_at')

    def get_serializer_context(self):
        return {'request': self.request}


class ReelListCreateView(APIView):
    def get(self, request, username=None):
        if username:
            user = get_object_or_404(User, username=username)
            reels = Reel.objects.filter(user=user, is_archived=False)
        else:
            reels = Reel.objects.filter(is_archived=False).order_by('-created_at')
        return Response(ReelSerializer(reels, many=True, context={'request': request}).data)

    def post(self, request):
        serializer = CreateReelSerializer(data=request.data)
        if serializer.is_valid():
            reel = serializer.save(user=request.user)
            return Response(ReelSerializer(reel, context={'request': request}).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReelDetailView(APIView):
    def get(self, request, pk):
        reel = get_object_or_404(Reel, pk=pk)
        # Increment view count
        Reel.objects.filter(pk=pk).update(view_count=reel.view_count + 1)
        return Response(ReelSerializer(reel, context={'request': request}).data)

    def put(self, request, pk):
        reel = get_object_or_404(Reel, pk=pk, user=request.user)
        serializer = CreateReelSerializer(reel, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(ReelSerializer(reel, context={'request': request}).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        return self.put(request, pk)

    def delete(self, request, pk):
        reel = get_object_or_404(Reel, pk=pk, user=request.user)
        reel.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ReelShareView(APIView):
    def post(self, request, pk):
        reel = get_object_or_404(Reel, pk=pk)
        Reel.objects.filter(pk=pk).update(share_count=reel.share_count + 1)
        return Response({'message': 'Share counted.'})
