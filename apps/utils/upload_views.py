from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .supabase_storage import upload_file

ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
ALLOWED_VIDEO_TYPES = ['video/mp4', 'video/quicktime', 'video/x-msvideo']
MAX_IMAGE_SIZE = 10 * 1024 * 1024
MAX_VIDEO_SIZE = 100 * 1024 * 1024


class UploadMediaView(APIView):
    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file provided.'}, status=status.HTTP_400_BAD_REQUEST)
        content_type = file.content_type
        is_image = content_type in ALLOWED_IMAGE_TYPES
        is_video = content_type in ALLOWED_VIDEO_TYPES
        if not (is_image or is_video):
            return Response({'error': f'Unsupported type: {content_type}'}, status=status.HTTP_400_BAD_REQUEST)
        max_size = MAX_IMAGE_SIZE if is_image else MAX_VIDEO_SIZE
        if file.size > max_size:
            return Response({'error': 'File too large.'}, status=status.HTTP_400_BAD_REQUEST)
        folder = request.data.get('folder', 'posts')
        try:
            url = upload_file(file, folder=folder)
            return Response({'url': url, 'media_type': 'image' if is_image else 'video'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
