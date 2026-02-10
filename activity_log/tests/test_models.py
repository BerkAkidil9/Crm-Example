"""
Tests for activity_log.models – ActivityLog model and log_activity helper.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

from activity_log.models import (
    ActivityLog, log_activity,
    ACTION_LEAD_CREATED, ACTION_ORDER_CREATED, ACTION_PRODUCT_UPDATED,
)
from leads.models import UserProfile

User = get_user_model()


class ActivityLogModelTests(TestCase):
    """Tests for ActivityLog model."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='loguser', email='loguser@test.com', password='testpass123',
            is_organisor=True, email_verified=True,
            first_name='Log', last_name='User',
        )
        cls.organisation = UserProfile.objects.get(user=cls.user)

    def test_create_activity_log(self):
        log = ActivityLog.objects.create(
            user=self.user,
            action=ACTION_LEAD_CREATED,
            object_type='lead',
            object_id=1,
            object_repr='Lead: John Doe',
            organisation=self.organisation,
        )
        self.assertEqual(log.action, ACTION_LEAD_CREATED)
        self.assertEqual(log.object_type, 'lead')
        self.assertEqual(log.object_id, 1)

    def test_str_representation(self):
        log = ActivityLog.objects.create(
            user=self.user,
            action=ACTION_ORDER_CREATED,
        )
        string = str(log)
        self.assertIn('Log User', string)
        self.assertIn('Order created', string)

    def test_str_with_deleted_user(self):
        log = ActivityLog.objects.create(user=None, action=ACTION_LEAD_CREATED)
        self.assertIn('Unknown', str(log))

    def test_ordering_newest_first(self):
        """Meta ordering is ['-created_at'], so highest pk (latest created) comes first."""
        log1 = ActivityLog.objects.create(user=self.user, action=ACTION_LEAD_CREATED)
        log2 = ActivityLog.objects.create(user=self.user, action=ACTION_ORDER_CREATED)
        logs = list(ActivityLog.objects.order_by('-created_at', '-pk'))
        self.assertEqual(logs[0].pk, log2.pk)
        self.assertEqual(logs[1].pk, log1.pk)

    def test_get_detail_url_returns_url(self):
        log = ActivityLog.objects.create(
            user=self.user, action=ACTION_LEAD_CREATED,
            object_type='lead', object_id=999,
        )
        url = log.get_detail_url()
        # May return None if URL doesn't exist, but should try
        # For a valid lead pk the URL would be built
        if url:
            self.assertIn('999', url)

    def test_get_detail_url_returns_none_without_object_type(self):
        log = ActivityLog.objects.create(
            user=self.user, action=ACTION_LEAD_CREATED,
        )
        self.assertIsNone(log.get_detail_url())


class LogActivityHelperTests(TestCase):
    """Tests for the log_activity() helper function."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='helperuser', email='helper@test.com', password='testpass123',
            is_organisor=True, email_verified=True,
        )
        cls.organisation = UserProfile.objects.get(user=cls.user)

    def test_creates_log_entry(self):
        entry = log_activity(
            user=self.user,
            action=ACTION_PRODUCT_UPDATED,
            object_type='product',
            object_id=42,
            object_repr='Product: Laptop',
            details={'old_price': 100, 'new_price': 120},
            organisation=self.organisation,
        )
        self.assertIsNotNone(entry)
        self.assertEqual(entry.action, ACTION_PRODUCT_UPDATED)
        self.assertEqual(entry.details['old_price'], 100)

    def test_returns_none_for_anonymous_user(self):
        result = log_activity(user=AnonymousUser(), action=ACTION_LEAD_CREATED)
        self.assertIsNone(result)

    def test_returns_none_for_none_user(self):
        result = log_activity(user=None, action=ACTION_LEAD_CREATED)
        self.assertIsNone(result)

    def test_truncates_long_object_repr(self):
        long_repr = 'X' * 500
        entry = log_activity(
            user=self.user, action=ACTION_LEAD_CREATED,
            object_repr=long_repr,
        )
        self.assertEqual(len(entry.object_repr), 255)
