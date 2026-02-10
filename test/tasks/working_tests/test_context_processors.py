"""
Tests for tasks.context_processors – notifications() context processor.
"""
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

from tasks.models import Task, Notification
from tasks.context_processors import notifications
from leads.models import UserProfile

User = get_user_model()


class TestNotificationsContextProcessor(TestCase):
    """Tests for the notifications() context processor."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='cpuser', email='cpuser@test.com', password='testpass123',
            is_organisor=True, email_verified=True,
        )
        cls.organisation = UserProfile.objects.get(user=cls.user)

    def setUp(self):
        self.factory = RequestFactory()

    def _make_request(self, user=None):
        request = self.factory.get('/')
        request.user = user or self.user
        return request

    # -- authenticated user tests --

    def test_authenticated_user_no_notifications(self):
        request = self._make_request()
        ctx = notifications(request)
        self.assertEqual(ctx['unread_notification_count'], 0)

    def test_authenticated_user_with_unread_notifications(self):
        Notification.objects.create(
            user=self.user, title='N1', message='M1',
            key='key-1', action_url='/', action_label='Go',
        )
        Notification.objects.create(
            user=self.user, title='N2', message='M2',
            key='key-2', action_url='/', action_label='Go',
        )
        request = self._make_request()
        ctx = notifications(request)
        self.assertEqual(ctx['unread_notification_count'], 2)

    def test_read_notifications_not_counted(self):
        Notification.objects.create(
            user=self.user, title='Read', message='M',
            key='key-read', action_url='/', action_label='Go', is_read=True,
        )
        Notification.objects.create(
            user=self.user, title='Unread', message='M',
            key='key-unread', action_url='/', action_label='Go', is_read=False,
        )
        request = self._make_request()
        ctx = notifications(request)
        self.assertEqual(ctx['unread_notification_count'], 1)

    def test_other_users_notifications_not_counted(self):
        other = User.objects.create_user(
            username='other', email='other@test.com', password='pass',
        )
        Notification.objects.create(
            user=other, title='Other', message='M',
            key='key-other', action_url='/', action_label='Go',
        )
        request = self._make_request(user=self.user)
        ctx = notifications(request)
        self.assertEqual(ctx['unread_notification_count'], 0)

    # -- anonymous user test --

    def test_anonymous_user_returns_zero(self):
        request = self._make_request(user=AnonymousUser())
        ctx = notifications(request)
        self.assertEqual(ctx['unread_notification_count'], 0)
