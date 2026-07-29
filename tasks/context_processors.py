from .models import Notification
import logging

logger = logging.getLogger(__name__)


def notifications(request):
    """Add unread notification count for the navbar."""
    if request.user.is_authenticated:
        try:
            return {
                'unread_notification_count': Notification.objects.filter(
                    user=request.user, is_read=False
                ).count(),
            }
        except Exception:
            logger.warning("Unread notification count failed", exc_info=True)
            return {'unread_notification_count': 0}
    return {'unread_notification_count': 0}
