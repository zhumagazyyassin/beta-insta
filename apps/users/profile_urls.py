from django.urls import path
from . import views

urlpatterns = [
    # Этот путь должен быть ПЕРВЫМ. Он отвечает за /api/users/
    path('', views.UserListView.as_view(), name='user-list'), 
    
    path('suggested/', views.SuggestedUsersView.as_view(), name='suggested-users'),
    path('<str:username>/', views.UserProfileView.as_view(), name='user-profile'),
    path('<str:username>/followers/', views.UserFollowersView.as_view(), name='user-followers'),
    path('<str:username>/following/', views.UserFollowingView.as_view(), name='user-following'),
]