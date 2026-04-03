import os
import uuid
from django.conf import settings

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False


def get_supabase_client():
    if not SUPABASE_AVAILABLE:
        raise ImportError("supabase package not installed")
    url = settings.SUPABASE_URL
    key = settings.SUPABASE_SERVICE_KEY or settings.SUPABASE_KEY
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")
    return create_client(url, key)


def upload_file(file_obj, folder='posts', filename=None):
    """Upload file to Supabase Storage, returns public URL."""
    client = get_supabase_client()
    bucket = settings.SUPABASE_STORAGE_BUCKET
    if not filename:
        ext = os.path.splitext(file_obj.name)[1] if hasattr(file_obj, 'name') else '.bin'
        filename = f"{uuid.uuid4()}{ext}"
    path = f"{folder}/{filename}"
    file_data = file_obj.read() if hasattr(file_obj, 'read') else file_obj
    client.storage.from_(bucket).upload(
        path=path,
        file=file_data,
        file_options={"content-type": getattr(file_obj, 'content_type', 'application/octet-stream')}
    )
    return client.storage.from_(bucket).get_public_url(path)


def delete_file(file_url):
    """Delete file from Supabase Storage by URL."""
    try:
        client = get_supabase_client()
        bucket = settings.SUPABASE_STORAGE_BUCKET
        base = f"{settings.SUPABASE_URL}/storage/v1/object/public/{bucket}/"
        path = file_url.replace(base, '')
        client.storage.from_(bucket).remove([path])
        return True
    except Exception:
        return False
