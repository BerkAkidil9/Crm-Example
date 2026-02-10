"""
Tests for tasks.context_processors – notifications() function.
(App-internal version of the test – mirrors test/tasks/working_tests/test_context_processors.py)
"""
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

from tasks.models import Notification
from tasks.context_processors import notifications
from leads.models import UserProfile

User = get_user_model()


class NotificationsContextProcessorTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='cpint', email='cpint@test.com', password='testpass123',
            is_organisor=True, email_verified=True,
        )
        UserProfile.objects.get(user=cls.user)

    def setUp(self):
        self.factory = RequestFactory()

    def _make_request(self, user=None):
        request = self.factory.get('/')
        request.user = user or self.user
        return request

    def test_zero_for_no_notifications(self):
        ctx = notifications(self._make_request())
        self.assertEqual(ctx['unread_notification_count'], 0)

    def test_counts_only_unread(self):
        Notification.objects.create(
            user=self.user, title='U', message='', key='cp-u',
            action_url='/', action_label='Go',
        )
        Notification.objects.create(
            user=self.user, title='R', message='', key='cp-r',
            action_url='/', action_label='Go', is_read=True,
        )
        ctx = notifications(self._make_request())
        self.assertEqual(ctx['unread_notification_count'], 1)

    def test_anonymous_user_returns_zero(self):
        ctx = notifications(self._make_request(user=AnonymousUser()))
        self.assertEqual(ctx['unread_notification_count'], 0)
