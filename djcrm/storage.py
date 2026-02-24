"""
R2 storage backend that saves to Cloudflare R2 but returns URLs via our app (media-proxy).
Use when pub-xxx.r2.dev is unreachable (e.g. ERR_CONNECTION_RESET) in your region.
Set USE_R2_MEDIA_PROXY=true to enable.
"""
from django.conf import settings
from storages.backends.s3 import S3Storage


class R2ProxyStorage(S3Storage):
    """Same as S3Storage for R2, but url() returns SITE_URL + /media-proxy/ + path."""

    def url(self, name):
        base = (getattr(settings, "SITE_URL", "") or "").rstrip("/")
        path = name.lstrip("/") if name else ""
        return f"{base}/media-proxy/{path}" if base and path else ""
