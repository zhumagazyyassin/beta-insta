from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth import get_user_model, authenticate
from django.shortcuts import get_object_or_404
from .serializers import (
    RegisterSerializer, UserPublicSerializer, UserPrivateSerializer,
    UpdateProfileSerializer, ChangePasswordSerializer, UserMiniSerializer
)
from apps.follows.models import Follow

User = get_user_model()


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


class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Logged out successfully.'})
        except Exception:
            return Response({'error': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)


class MeView(APIView):
    def get(self, request):
        return Response(UserPrivateSerializer(request.user).data)

    def put(self, request):
        serializer = UpdateProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(UserPrivateSerializer(request.user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        return self.put(request)


class ChangePasswordView(APIView):
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            if not request.user.check_password(serializer.validated_data['old_password']):
                return Response({'error': 'Old password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)
            request.user.set_password(serializer.validated_data['new_password'])
            request.user.save()
            return Response({'message': 'Password changed successfully.'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        serializer = UserPublicSerializer(user, context={'request': request})
        return Response(serializer.data)


class UserFollowersView(generics.ListAPIView):
    serializer_class = UserMiniSerializer

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        follower_ids = Follow.objects.filter(following=user, status='accepted').values_list('follower_id', flat=True)
        return User.objects.filter(id__in=follower_ids)


class UserFollowingView(generics.ListAPIView):
    serializer_class = UserMiniSerializer

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        following_ids = Follow.objects.filter(follower=user, status='accepted').values_list('following_id', flat=True)
        return User.objects.filter(id__in=following_ids)


class SuggestedUsersView(APIView):
    def get(self, request):
        following_ids = Follow.objects.filter(
            follower=request.user, status='accepted'
        ).values_list('following_id', flat=True)
        suggested = User.objects.exclude(
            id__in=list(following_ids) + [request.user.id]
        ).order_by('?')[:10]
        return Response(UserMiniSerializer(suggested, many=True, context={'request': request}).data)
