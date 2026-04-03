from django.urls import path
from . import views

urlpatterns = [
    path('', views.SearchView.as_view(), name='search'),
    path('users/', views.SearchUsersView.as_view(), name='search-users'),
    path('trending/', views.TrendingHashtagsView.as_view(), name='trending-hashtags'),
]
