from django.urls import path
from . import views

urlpatterns = [
    path('post/<uuid:post_id>/', views.PostCommentsView.as_view(), name='post-comments'),
    path('reel/<uuid:reel_id>/', views.ReelCommentsView.as_view(), name='reel-comments'),
    path('<uuid:pk>/', views.CommentDetailView.as_view(), name='comment-detail'),
    path('<uuid:pk>/replies/', views.CommentRepliesView.as_view(), name='comment-replies'),
]
