"""
Tests for activity_log.views – ActivityLogListView.
"""
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model

from activity_log.models import ActivityLog, ACTION_LEAD_CREATED, ACTION_ORDER_CREATED
from leads.models import UserProfile, Agent

User = get_user_model()

SIMPLE_STATIC = {
    'STATICFILES_STORAGE': 'django.contrib.staticfiles.storage.StaticFilesStorage',
}


@override_settings(**SIMPLE_STATIC)
class ActivityLogListViewTests(TestCase):
    """Tests for ActivityLogListView (auth, permission-based filtering, template)."""

    @classmethod
    def setUpTestData(cls):
        # Admin
        cls.admin = User.objects.create_superuser(
            username='actadmin', email='actadmin@test.com', password='testpass123',
        )
        # Organisor
        cls.organisor_user = User.objects.create_user(
            username='actorg', email='actorg@test.com', password='testpass123',
            is_organisor=True, email_verified=True,
        )
        cls.organisation = UserProfile.objects.get(user=cls.organisor_user)
        # Agent
        cls.agent_user = User.objects.create_user(
            username='actagent', email='actagent@test.com', password='testpass123',
            is_agent=True, email_verified=True,
        )
        cls.agent = Agent.objects.create(user=cls.agent_user, organisation=cls.organisation)

        # Create some logs
        cls.org_log = ActivityLog.objects.create(
            user=cls.organisor_user, action=ACTION_LEAD_CREATED,
            object_type='lead', organisation=cls.organisation,
        )
        cls.agent_log = ActivityLog.objects.create(
            user=cls.agent_user, action=ACTION_ORDER_CREATED,
            object_type='order', organisation=cls.organisation,
            affected_agent=cls.agent,
        )

    def setUp(self):
        self.client = Client()
        self.url = reverse('activity_log:activity-log-list')

    def test_anonymous_user_redirected(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.url)

    def test_admin_sees_all_logs(self):
        self.client.force_login(self.admin)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.context['activity_logs']), 2)

    def test_organisor_sees_own_and_organisation_logs(self):
        self.client.force_login(self.organisor_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        log_pks = [l.pk for l in response.context['activity_logs']]
        self.assertIn(self.org_log.pk, log_pks)

    def test_uses_correct_template(self):
        self.client.force_login(self.admin)
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'activity_log/activity_log_list.html')
