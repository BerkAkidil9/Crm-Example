from .models import Notification


def notifications(request):
    """Add unread notification count for the navbar."""
    if request.user.is_authenticated:
        return {
            'unread_notification_count': Notification.objects.filter(
                user=request.user, is_read=False
            ).count(),
        }
    return {'unread_notification_count': 0}
