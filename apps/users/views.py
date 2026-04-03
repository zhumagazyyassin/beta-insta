from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model, authenticate
from django.shortcuts import get_object_or_404

from .serializers import (
    RegisterSerializer, UserPublicSerializer, UserPrivateSerializer,
    UpdateProfileSerializer, ChangePasswordSerializer, UserMiniSerializer
)
from apps.follows.models import Follow

User = get_user_model()

# --- НОВЫЙ КЛАСС (СПИСОК ПОЛЬЗОВАТЕЛЕЙ) ---
class UserListView(generics.ListAPIView):
    """
    Представление для получения списка всех зарегистрированных пользователей.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserMiniSerializer
    permission_classes = [permissions.IsAuthenticated]

# --- ОСТАЛЬНЫЕ КЛАССЫ ---
class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserPrivateSerializer(user).data,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        if not email or not password:
            return Response({'error': 'Email and password required.'}, status=status.HTTP_400_BAD_REQUEST)
        user = authenticate(request, username=email, password=password)
        if not user:
            return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserPrivateSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })

class MeView(APIView):
    def get(self, request):
        return Response(UserPrivateSerializer(request.user).data)

class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        serializer = UserPublicSerializer(user, context={'request': request})
        return Response(serializer.data)

class SuggestedUsersView(APIView):
    def get(self, request):
        following_ids = Follow.objects.filter(
            follower=request.user, status='accepted'
        ).values_list('following_id', flat=True)
        suggested = User.objects.exclude(
            id__in=list(following_ids) + [request.user.id]
        ).order_by('?')[:10]
        return Response(UserMiniSerializer(suggested, many=True, context={'request': request}).data)