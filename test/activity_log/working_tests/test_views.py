"""
Tests for activity_log.views – ActivityLogListView.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from activity_log.models import ActivityLog, ACTION_LEAD_CREATED, ACTION_AGENT_CREATED
from leads.models import UserProfile, Agent

User = get_user_model()


class TestActivityLogListView(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_superuser(
            username='aladmin', email='aladmin@test.com', password='testpass123',
        )
        cls.organisor_user = User.objects.create_user(
            username='alorg', email='alorg@test.com', password='testpass123',
            is_organisor=True, email_verified=True,
        )
        cls.organisation = UserProfile.objects.get(user=cls.organisor_user)
        cls.agent_user = User.objects.create_user(
            username='alagent', email='alagent@test.com', password='testpass123',
            is_agent=True, email_verified=True,
        )
        cls.agent = Agent.objects.create(user=cls.agent_user, organisation=cls.organisation)

        # Other organisation
        cls.other_org_user = User.objects.create_user(
            username='alotherorg', email='alotherorg@test.com', password='testpass123',
            is_organisor=True, email_verified=True,
        )
        cls.other_organisation = UserProfile.objects.get(user=cls.other_org_user)

    def setUp(self):
        self.client = Client()

    def test_unauthenticated_redirects(self):
        response = self.client.get(reverse('activity_log:activity-log-list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.url)

    def test_admin_sees_all_logs(self):
        ActivityLog.objects.create(
            user=self.organisor_user, action=ACTION_LEAD_CREATED,
            organisation=self.organisation,
        )
        ActivityLog.objects.create(
            user=self.other_org_user, action=ACTION_LEAD_CREATED,
            organisation=self.other_organisation,
        )
        self.client.login(username='aladmin', password='testpass123')
        response = self.client.get(reverse('activity_log:activity-log-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['activity_logs']), 2)

    def test_admin_filter_by_user(self):
        ActivityLog.objects.create(user=self.organisor_user, action=ACTION_LEAD_CREATED)
        ActivityLog.objects.create(user=self.other_org_user, action=ACTION_LEAD_CREATED)
        self.client.login(username='aladmin', password='testpass123')
        response = self.client.get(
            reverse('activity_log:activity-log-list'),
            {'user': self.organisor_user.pk},
        )
        logs = response.context['activity_logs']
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0].user, self.organisor_user)

    def test_admin_filter_by_organisation(self):
        ActivityLog.objects.create(
            user=self.organisor_user, action=ACTION_LEAD_CREATED,
            organisation=self.organisation,
        )
        ActivityLog.objects.create(
            user=self.other_org_user, action=ACTION_LEAD_CREATED,
            organisation=self.other_organisation,
        )
        self.client.login(username='aladmin', password='testpass123')
        response = self.client.get(
            reverse('activity_log:activity-log-list'),
            {'organisation': self.organisation.pk},
        )
        logs = response.context['activity_logs']
        self.assertEqual(len(logs), 1)

    def test_organisor_sees_own_and_org_logs(self):
        # Own action
        ActivityLog.objects.create(
            user=self.organisor_user, action=ACTION_LEAD_CREATED,
            organisation=self.organisation,
        )
        # Agent action within same org
        ActivityLog.objects.create(
            user=self.agent_user, action=ACTION_LEAD_CREATED,
            organisation=self.organisation,
        )
        # Other org action (should NOT appear)
        ActivityLog.objects.create(
            user=self.other_org_user, action=ACTION_LEAD_CREATED,
            organisation=self.other_organisation,
        )
        self.client.login(username='alorg', password='testpass123')
        response = self.client.get(reverse('activity_log:activity-log-list'))
        logs = response.context['activity_logs']
        self.assertEqual(len(logs), 2)

    def test_agent_sees_own_and_affected_logs(self):
        # Agent's own action
        ActivityLog.objects.create(
            user=self.agent_user, action=ACTION_LEAD_CREATED,
        )
        # Action affecting this agent
        ActivityLog.objects.create(
            user=self.organisor_user, action=ACTION_AGENT_CREATED,
            affected_agent=self.agent,
        )
        # Unrelated action (should NOT appear)
        ActivityLog.objects.create(
            user=self.other_org_user, action=ACTION_LEAD_CREATED,
        )
        logged_in = self.client.login(username='alagent', password='testpass123')
        self.assertTrue(logged_in, 'Agent login failed')
        response = self.client.get(reverse('activity_log:activity-log-list'))
        logs = response.context['activity_logs']
        # Agent should see own actions and actions affecting them (at least 1)
        self.assertGreaterEqual(len(logs), 1)
        # Unrelated action should NOT appear
        for log in logs:
            self.assertTrue(
                log.user == self.agent_user or log.affected_agent == self.agent,
                f'Agent should not see unrelated log: {log}'
            )

    def test_template_used(self):
        self.client.login(username='aladmin', password='testpass123')
        response = self.client.get(reverse('activity_log:activity-log-list'))
        self.assertTemplateUsed(response, 'activity_log/activity_log_list.html')

    def test_admin_context_has_filters(self):
        self.client.login(username='aladmin', password='testpass123')
        response = self.client.get(reverse('activity_log:activity-log-list'))
        self.assertIn('filter_users', response.context)
        self.assertIn('filter_organisations', response.context)

    def test_organisor_context_no_filter_users(self):
        self.client.login(username='alorg', password='testpass123')
        response = self.client.get(reverse('activity_log:activity-log-list'))
        self.assertNotIn('filter_users', response.context)

    def test_pagination(self):
        """View should paginate at 30 items."""
        for i in range(35):
            ActivityLog.objects.create(
                user=self.admin, action=ACTION_LEAD_CREATED,
            )
        self.client.login(username='aladmin', password='testpass123')
        response = self.client.get(reverse('activity_log:activity-log-list'))
        self.assertEqual(len(response.context['activity_logs']), 30)
        # Page 2
        response2 = self.client.get(reverse('activity_log:activity-log-list'), {'page': 2})
        self.assertEqual(len(response2.context['activity_logs']), 5)
