from django.urls import path
from . import views

urlpatterns = [
    path('<str:username>/', views.FollowView.as_view(), name='follow'),
    path('<str:username>/accept/', views.AcceptFollowRequestView.as_view(), name='accept-follow'),
    path('<str:username>/remove/', views.RemoveFollowerView.as_view(), name='remove-follower'),
    path('requests/pending/', views.PendingRequestsView.as_view(), name='pending-requests'),
    path('block/<str:username>/', views.BlockView.as_view(), name='block-user'),
    path('blocked/', views.BlockedUsersView.as_view(), name='blocked-users'),
]
