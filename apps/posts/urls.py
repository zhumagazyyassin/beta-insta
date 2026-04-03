from django.urls import path
from . import views

urlpatterns = [
    path('feed/', views.FeedView.as_view(), name='feed'),
    path('explore/', views.ExploreFeedView.as_view(), name='explore'),
    path('', views.PostListCreateView.as_view(), name='post-create'),
    path('<uuid:pk>/', views.PostDetailView.as_view(), name='post-detail'),
    path('user/<str:username>/', views.PostListCreateView.as_view(), name='user-posts'),
    path('saved/', views.SavedPostsView.as_view(), name='saved-posts'),
    path('<uuid:pk>/save/', views.SavePostView.as_view(), name='save-post'),
    path('collections/', views.CollectionListCreateView.as_view(), name='collections'),
    path('collections/<uuid:pk>/', views.CollectionDetailView.as_view(), name='collection-detail'),
    path('collections/<uuid:pk>/posts/<uuid:post_id>/', views.AddToCollectionView.as_view(), name='collection-post'),
    path('hashtag/<str:name>/', views.HashtagPostsView.as_view(), name='hashtag-posts'),
    path('archived/', views.ArchivedPostsView.as_view(), name='archived-posts'),
    path('<uuid:pk>/archive/', views.ArchivePostView.as_view(), name='archive-post'),
]
