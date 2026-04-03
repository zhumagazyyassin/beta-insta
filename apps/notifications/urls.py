from django.urls import path
from . import views

urlpatterns = [
    path('', views.NotificationListView.as_view(), name='notifications'),
    path('unread/', views.UnreadCountView.as_view(), name='unread-count'),
    path('mark-read/', views.MarkReadView.as_view(), name='mark-all-read'),
    path('<uuid:pk>/mark-read/', views.MarkReadView.as_view(), name='mark-read'),
    path('<uuid:pk>/', views.DeleteNotificationView.as_view(), name='delete-notification'),
]
