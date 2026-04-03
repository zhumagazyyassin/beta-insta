from django.urls import path
from . import views

urlpatterns = [
    path('feed/', views.StoryFeedView.as_view(), name='story-feed'),
    path('', views.StoryCreateView.as_view(), name='story-create'),
    path('<uuid:pk>/', views.StoryDetailView.as_view(), name='story-detail'),
    path('<uuid:pk>/viewers/', views.StoryViewersView.as_view(), name='story-viewers'),
    path('<uuid:pk>/react/', views.StoryReactionView.as_view(), name='story-react'),
    path('user/<str:username>/', views.UserStoriesView.as_view(), name='user-stories'),
    path('highlights/', views.HighlightListCreateView.as_view(), name='highlight-create'),
    path('highlights/user/<str:username>/', views.HighlightListCreateView.as_view(), name='user-highlights'),
    path('highlights/<uuid:pk>/', views.HighlightDetailView.as_view(), name='highlight-detail'),
]
