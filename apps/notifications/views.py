from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Notification
from .serializers import NotificationSerializer


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).select_related(
            'sender', 'post', 'reel', 'comment', 'story'
        )


class MarkReadView(APIView):
    def post(self, request, pk=None):
        if pk:
            notif = Notification.objects.filter(pk=pk, recipient=request.user).first()
            if notif:
                notif.is_read = True
                notif.save()
        else:
            Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        return Response({'message': 'Marked as read.'})


class UnreadCountView(APIView):
    def get(self, request):
        count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        return Response({'unread_count': count})


class DeleteNotificationView(APIView):
    def delete(self, request, pk):
        Notification.objects.filter(pk=pk, recipient=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
