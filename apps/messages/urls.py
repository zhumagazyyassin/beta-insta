from django.urls import path
from . import views

urlpatterns = [
    path('', views.ChatListView.as_view(), name='chats'),
    path('<uuid:pk>/', views.ChatDetailView.as_view(), name='chat-detail'),
    path('<uuid:chat_id>/messages/', views.MessageListView.as_view(), name='chat-messages'),
    path('<uuid:chat_id>/messages/<uuid:pk>/', views.MessageDetailView.as_view(), name='message-detail'),
    path('<uuid:chat_id>/messages/<uuid:pk>/react/', views.MessageReactionView.as_view(), name='message-react'),
]
