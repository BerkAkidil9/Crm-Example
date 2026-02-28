"""
Media proxy view: serve R2 (or default storage) files through the app.
Used when USE_R2_MEDIA_PROXY=true to avoid ERR_CONNECTION_RESET to pub-xxx.r2.dev.
Access is restricted by path: lead_photos/ and profile_images/ require the user
to have permission to the owning lead or user (IDOR prevention).
"""
import logging
import mimetypes
from django.http import FileResponse, Http404
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage

logger = logging.getLogger(__name__)


def _user_can_access_media_path(user, path):
    """
    Return True if the user is allowed to access the file at path.
    lead_photos/ and profile_images/ are restricted by organisation/agent ownership.
    """
    from leads.models import Lead, User, Agent

    if path.startswith("lead_photos/"):
        leads = Lead.objects.filter(profile_image=path)
        for lead in leads:
            if user.is_superuser:
                return True
            if getattr(user, "is_organisor", False) and getattr(user, "userprofile", None):
                if lead.organisation_id == user.userprofile.id:
                    return True
            if getattr(user, "is_agent", False):
                try:
                    agent_obj = Agent.objects.get(user=user)
                    if lead.agent_id == agent_obj.id:
                        return True
                except Agent.DoesNotExist:
                    pass
        return False

    if path.startswith("profile_images/"):
        users_with_path = User.objects.filter(profile_image=path)
        for profile_user in users_with_path:
            if profile_user.id == user.id:
                return True
            if user.is_superuser:
                return True
            if getattr(user, "is_organisor", False) and getattr(user, "userprofile", None):
                # Organisor can see agents in their org (agent.user.profile_image)
                try:
                    agent_obj = Agent.objects.get(user=profile_user)
                    if agent_obj.organisation_id == user.userprofile.id:
                        return True
                except Agent.DoesNotExist:
                    pass
        return False

    # Unknown path prefix: deny by default (only allow known media types)
    return False


@require_GET
@login_required
@cache_control(public=True, max_age=86400)  # 1 day
def media_proxy(request, path: str):
    """Stream a file from default storage (R2 or filesystem) by path. Path must not contain '..'."""
    if ".." in path or path.startswith("/"):
        raise Http404("Invalid path")
    if not _user_can_access_media_path(request.user, path):
        raise Http404("File not found")
    if not default_storage.exists(path):
        raise Http404("File not found")
    try:
        f = default_storage.open(path, "rb")
        content_type, _ = mimetypes.guess_type(path)
        if not content_type:
            content_type = "application/octet-stream"
        return FileResponse(f, content_type=content_type)
    except FileNotFoundError:
        raise Http404("File not found")
    except Exception:
        logger.exception("Media proxy error for path=%s", path)
        raise Http404("File not found")
