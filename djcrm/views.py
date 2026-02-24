"""
Media proxy view: serve R2 (or default storage) files through the app.
Used when USE_R2_MEDIA_PROXY=true to avoid ERR_CONNECTION_RESET to pub-xxx.r2.dev.
"""
import mimetypes
from django.http import FileResponse, Http404
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_GET
from django.core.files.storage import default_storage


@require_GET
@cache_control(public=True, max_age=86400)  # 1 day
def media_proxy(request, path: str):
    """Stream a file from default storage (R2 or filesystem) by path. Path must not contain '..'."""
    if ".." in path or path.startswith("/"):
        raise Http404("Invalid path")
    if not default_storage.exists(path):
        raise Http404("File not found")
    try:
        f = default_storage.open(path, "rb")
        content_type, _ = mimetypes.guess_type(path)
        if not content_type:
            content_type = "application/octet-stream"
        return FileResponse(f, content_type=content_type)
    except Exception:
        raise Http404("File not found")
