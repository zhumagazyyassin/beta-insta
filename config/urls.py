from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from apps.utils.upload_views import UploadMediaView


def health_check(request):
    return JsonResponse({'status': 'ok', 'service': 'instagram-backend'})


urlpatterns = [
    path('api/health/', health_check, name='health-check'),
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.users.urls')),
    path('api/users/', include('apps.users.profile_urls')),
    path('api/posts/', include('apps.posts.urls')),
    path('api/stories/', include('apps.stories.urls')),
    path('api/reels/', include('apps.reels.urls')),
    path('api/comments/', include('apps.comments.urls')),
    path('api/likes/', include('apps.likes.urls')),
    path('api/follows/', include('apps.follows.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
    path('api/messages/', include('apps.messages.urls')),
    path('api/search/', include('apps.search.urls')),
    path('api/upload/', UploadMediaView.as_view(), name='upload-media'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
