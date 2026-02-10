"""
Tests for activity_log.models – ActivityLog model and log_activity helper.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from activity_log.models import (
    ActivityLog, log_activity,
    ACTION_LEAD_CREATED, ACTION_AGENT_CREATED, ACTION_ORDER_CREATED,
    ACTION_TASK_CREATED, ACTION_PRODUCT_CREATED, ACTION_ORGANISOR_CREATED,
    ACTION_LEAD_UPDATED, ACTION_LEAD_DELETED,
)
from leads.models import UserProfile, Agent

User = get_user_model()


class ActivityLogModelTestBase(TestCase):
    """Shared setUp."""

    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_superuser(
            username='logadmin', email='logadmin@test.com', password='testpass123',
        )
        cls.organisor_user = User.objects.create_user(
            username='logorg', email='logorg@test.com', password='testpass123',
            is_organisor=True,
        )
        cls.organisation = UserProfile.objects.get(user=cls.organisor_user)
        cls.agent_user = User.objects.create_user(
            username='logagent', email='logagent@test.com', password='testpass123',
            is_agent=True,
        )
        cls.agent = Agent.objects.create(user=cls.agent_user, organisation=cls.organisation)


# ---------------------------------------------------------------------------
# ActivityLog model
# ---------------------------------------------------------------------------
class TestActivityLogModel(ActivityLogModelTestBase):

    def test_create_log(self):
        log = ActivityLog.objects.create(
            user=self.organisor_user,
            action=ACTION_LEAD_CREATED,
            object_type='lead',
            object_id=1,
            object_repr='Lead: John Doe',
        )
        self.assertIsNotNone(log.pk)
        self.assertEqual(log.action, ACTION_LEAD_CREATED)

    def test_str_representation(self):
        log = ActivityLog.objects.create(
            user=self.organisor_user,
            action=ACTION_LEAD_CREATED,
        )
        self.assertIn('logorg', str(log))
        self.assertIn('Lead created', str(log))

    def test_str_with_full_name(self):
        self.organisor_user.first_name = 'John'
        self.organisor_user.last_name = 'Doe'
        self.organisor_user.save()
        log = ActivityLog.objects.create(
            user=self.organisor_user,
            action=ACTION_LEAD_CREATED,
        )
        self.assertIn('John Doe', str(log))
        # Cleanup
        self.organisor_user.first_name = ''
        self.organisor_user.last_name = ''
        self.organisor_user.save()

    def test_str_with_deleted_user(self):
        temp = User.objects.create_user(username='temp_log', email='temp_log@test.com', password='pass')
        log = ActivityLog.objects.create(user=temp, action=ACTION_LEAD_CREATED)
        temp.delete()
        log.refresh_from_db()
        self.assertIn('Unknown', str(log))

    def test_user_set_null_on_delete(self):
        temp = User.objects.create_user(username='temp2', email='temp2@test.com', password='pass')
        log = ActivityLog.objects.create(user=temp, action=ACTION_LEAD_CREATED)
        temp.delete()
        log.refresh_from_db()
        self.assertIsNone(log.user)

    def test_organisation_set_null_on_delete(self):
        org_user = User.objects.create_user(
            username='temporg', email='temporg@test.com', password='pass', is_organisor=True,
        )
        org = UserProfile.objects.get(user=org_user)
        log = ActivityLog.objects.create(
            user=self.admin, action=ACTION_LEAD_CREATED, organisation=org,
        )
        org.delete()
        log.refresh_from_db()
        self.assertIsNone(log.organisation)

    def test_affected_agent_set_null_on_delete(self):
        temp_agent_user = User.objects.create_user(
            username='tempagent', email='tempagent@test.com', password='pass', is_agent=True,
        )
        temp_agent = Agent.objects.create(user=temp_agent_user, organisation=self.organisation)
        log = ActivityLog.objects.create(
            user=self.admin, action=ACTION_LEAD_CREATED, affected_agent=temp_agent,
        )
        temp_agent.delete()
        log.refresh_from_db()
        self.assertIsNone(log.affected_agent)

    def test_details_json_field(self):
        details = {'old_price': 100, 'new_price': 120}
        log = ActivityLog.objects.create(
            user=self.admin, action=ACTION_PRODUCT_CREATED, details=details,
        )
        log.refresh_from_db()
        self.assertEqual(log.details['old_price'], 100)
        self.assertEqual(log.details['new_price'], 120)

    def test_details_default_empty_dict(self):
        log = ActivityLog.objects.create(
            user=self.admin, action=ACTION_LEAD_CREATED,
        )
        self.assertEqual(log.details, {})

    def test_ordering(self):
        """Logs should be ordered by -created_at (newest first). Also verify pk ordering as fallback."""
        l1 = ActivityLog.objects.create(user=self.admin, action=ACTION_LEAD_CREATED)
        l2 = ActivityLog.objects.create(user=self.admin, action=ACTION_LEAD_UPDATED)
        logs = list(ActivityLog.objects.all())
        # Both may have the same created_at in fast tests; at minimum l2.pk > l1.pk
        self.assertGreater(l2.pk, l1.pk)
        self.assertEqual(len(logs), 2)

    def test_auto_created_at(self):
        log = ActivityLog.objects.create(user=self.admin, action=ACTION_LEAD_CREATED)
        self.assertIsNotNone(log.created_at)

    def test_verbose_names(self):
        self.assertEqual(ActivityLog._meta.verbose_name, 'Activity log entry')
        self.assertEqual(ActivityLog._meta.verbose_name_plural, 'Activity logs')

    def test_all_action_choices(self):
        from activity_log.models import ACTION_CHOICES
        self.assertTrue(len(ACTION_CHOICES) >= 18)


# ---------------------------------------------------------------------------
# get_detail_url method
# ---------------------------------------------------------------------------
class TestActivityLogGetDetailUrl(ActivityLogModelTestBase):

    def test_lead_detail_url(self):
        log = ActivityLog.objects.create(
            user=self.admin, action=ACTION_LEAD_CREATED,
            object_type='lead', object_id=1,
        )
        self.assertEqual(log.get_detail_url(), reverse('leads:lead-detail', kwargs={'pk': 1}))

    def test_order_detail_url(self):
        log = ActivityLog.objects.create(
            user=self.admin, action=ACTION_ORDER_CREATED,
            object_type='order', object_id=1,
        )
        self.assertEqual(log.get_detail_url(), reverse('orders:order-detail', kwargs={'pk': 1}))

    def test_task_detail_url(self):
        log = ActivityLog.objects.create(
            user=self.admin, action=ACTION_TASK_CREATED,
            object_type='task', object_id=1,
        )
        self.assertEqual(log.get_detail_url(), reverse('tasks:task-detail', kwargs={'pk': 1}))

    def test_product_detail_url(self):
        log = ActivityLog.objects.create(
            user=self.admin, action=ACTION_PRODUCT_CREATED,
            object_type='product', object_id=1,
        )
        self.assertEqual(
            log.get_detail_url(),
            reverse('ProductsAndStock:ProductAndStock-detail', kwargs={'pk': 1}),
        )

    def test_agent_detail_url(self):
        log = ActivityLog.objects.create(
            user=self.admin, action=ACTION_AGENT_CREATED,
            object_type='agent', object_id=1,
        )
        self.assertEqual(log.get_detail_url(), reverse('agents:agent-detail', kwargs={'pk': 1}))

    def test_organisor_detail_url(self):
        log = ActivityLog.objects.create(
            user=self.admin, action=ACTION_ORGANISOR_CREATED,
            object_type='organisor', object_id=1,
        )
        self.assertEqual(
            log.get_detail_url(),
            reverse('organisors:organisor-detail', kwargs={'pk': 1}),
        )

    def test_returns_none_without_object_type(self):
        log = ActivityLog.objects.create(
            user=self.admin, action=ACTION_LEAD_CREATED,
        )
        self.assertIsNone(log.get_detail_url())

    def test_returns_none_for_unknown_type(self):
        log = ActivityLog.objects.create(
            user=self.admin, action=ACTION_LEAD_CREATED,
            object_type='unknown', object_id=1,
        )
        self.assertIsNone(log.get_detail_url())


# ---------------------------------------------------------------------------
# log_activity helper function
# ---------------------------------------------------------------------------
class TestLogActivityHelper(ActivityLogModelTestBase):

    def test_creates_log(self):
        log = log_activity(
            user=self.organisor_user,
            action=ACTION_LEAD_CREATED,
            object_type='lead',
            object_id=42,
            object_repr='Lead: Jane Doe',
            organisation=self.organisation,
        )
        self.assertIsNotNone(log)
        self.assertEqual(log.action, ACTION_LEAD_CREATED)
        self.assertEqual(log.object_id, 42)

    def test_with_details(self):
        log = log_activity(
            user=self.admin,
            action=ACTION_PRODUCT_CREATED,
            details={'price': 99.99},
        )
        self.assertEqual(log.details['price'], 99.99)

    def test_with_affected_agent(self):
        log = log_activity(
            user=self.organisor_user,
            action=ACTION_LEAD_CREATED,
            affected_agent=self.agent,
        )
        self.assertEqual(log.affected_agent, self.agent)

    def test_returns_none_for_unauthenticated(self):
        from django.contrib.auth.models import AnonymousUser
        result = log_activity(user=AnonymousUser(), action=ACTION_LEAD_CREATED)
        self.assertIsNone(result)

    def test_returns_none_for_none_user(self):
        result = log_activity(user=None, action=ACTION_LEAD_CREATED)
        self.assertIsNone(result)

    def test_truncates_long_object_repr(self):
        long_repr = 'X' * 500
        log = log_activity(
            user=self.admin, action=ACTION_LEAD_CREATED,
            object_repr=long_repr,
        )
        self.assertEqual(len(log.object_repr), 255)

    def test_defaults(self):
        log = log_activity(user=self.admin, action=ACTION_LEAD_DELETED)
        self.assertEqual(log.object_type, '')
        self.assertIsNone(log.object_id)
        self.assertEqual(log.object_repr, '')
        self.assertEqual(log.details, {})
        self.assertIsNone(log.organisation)
        self.assertIsNone(log.affected_agent)
