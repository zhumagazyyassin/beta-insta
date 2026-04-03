from django.urls import path
from . import views

urlpatterns = [
    path('feed/', views.ReelFeedView.as_view(), name='reel-feed'),
    path('', views.ReelListCreateView.as_view(), name='reel-create'),
    path('<uuid:pk>/', views.ReelDetailView.as_view(), name='reel-detail'),
    path('<uuid:pk>/share/', views.ReelShareView.as_view(), name='reel-share'),
    path('user/<str:username>/', views.ReelListCreateView.as_view(), name='user-reels'),
]
