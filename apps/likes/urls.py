from django.urls import path
from . import views

urlpatterns = [
    path('post/<uuid:pk>/', views.LikePostView.as_view(), name='like-post'),
    path('post/<uuid:pk>/likers/', views.PostLikersView.as_view(), name='post-likers'),
    path('reel/<uuid:pk>/', views.LikeReelView.as_view(), name='like-reel'),
    path('reel/<uuid:pk>/likers/', views.ReelLikersView.as_view(), name='reel-likers'),
    path('comment/<uuid:pk>/', views.LikeCommentView.as_view(), name='like-comment'),
]
