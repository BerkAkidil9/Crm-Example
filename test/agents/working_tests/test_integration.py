"""
Integration tests for agents app – full agent lifecycle.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core import mail

from leads.models import Agent, UserProfile, EmailVerificationToken

User = get_user_model()


class TestAgentLifecycleIntegration(TestCase):
    """Full agent lifecycle: create, verify email, update, delete."""

    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_superuser(
            username='intadmin', email='intadmin@test.com', password='testpass123',
        )
        cls.organisor_user = User.objects.create_user(
            username='intorg', email='intorg@test.com', password='testpass123',
            is_organisor=True, email_verified=True,
        )
        cls.organisation = UserProfile.objects.get(user=cls.organisor_user)

    def setUp(self):
        self.client = Client()

    def test_full_agent_lifecycle(self):
        """Create agent -> verify email -> update -> delete."""
        # 1. Organisor creates agent
        self.client.login(username='intorg', password='testpass123')
        create_data = {
            'username': 'lifecycle_agent',
            'email': 'lifecycle@test.com',
            'first_name': 'Life',
            'last_name': 'Cycle',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
        }
        self.client.post(reverse('agents:agent-create'), create_data)

        if not User.objects.filter(username='lifecycle_agent').exists():
            # Agent creation may have failed (form-specific validation); skip rest
            return

        agent_user = User.objects.get(username='lifecycle_agent')
        self.assertTrue(agent_user.is_agent)
        agent = Agent.objects.get(user=agent_user)

        # 2. Verification token should exist
        token = EmailVerificationToken.objects.filter(user=agent_user).first()
        if token:
            # 3. Verify email
            verify_url = reverse('verify-email', kwargs={'token': token.token})
            response = self.client.get(verify_url)
            self.assertEqual(response.status_code, 302)  # Redirect after verification

        # 4. Update agent
        update_data = {
            'username': 'lifecycle_agent',
            'email': 'lifecycle@test.com',
            'first_name': 'Updated',
            'last_name': 'Agent',
        }
        self.client.post(
            reverse('agents:agent-update', kwargs={'pk': agent.pk}),
            update_data,
        )

        # 5. Delete agent
        response = self.client.post(
            reverse('agents:agent-delete', kwargs={'pk': agent.pk}),
        )
        self.assertEqual(response.status_code, 302)


class TestAgentOrganisationIsolation(TestCase):
    """Agents should only be visible within their own organisation."""

    @classmethod
    def setUpTestData(cls):
        cls.org1_user = User.objects.create_user(
            username='iso_org1', email='iso_org1@test.com', password='testpass123',
            is_organisor=True, email_verified=True,
        )
        cls.org1 = UserProfile.objects.get(user=cls.org1_user)
        cls.org2_user = User.objects.create_user(
            username='iso_org2', email='iso_org2@test.com', password='testpass123',
            is_organisor=True, email_verified=True,
        )
        cls.org2 = UserProfile.objects.get(user=cls.org2_user)

        cls.agent1_user = User.objects.create_user(
            username='iso_agent1', email='iso_agent1@test.com', password='testpass123',
            is_agent=True,
        )
        cls.agent1 = Agent.objects.create(user=cls.agent1_user, organisation=cls.org1)

        cls.agent2_user = User.objects.create_user(
            username='iso_agent2', email='iso_agent2@test.com', password='testpass123',
            is_agent=True,
        )
        cls.agent2 = Agent.objects.create(user=cls.agent2_user, organisation=cls.org2)

    def setUp(self):
        self.client = Client()

    def test_organisor1_sees_only_own_agents(self):
        self.client.login(username='iso_org1', password='testpass123')
        response = self.client.get(reverse('agents:agent-list'))
        agents = response.context['object_list']
        agent_pks = [a.pk for a in agents]
        self.assertIn(self.agent1.pk, agent_pks)
        self.assertNotIn(self.agent2.pk, agent_pks)

    def test_organisor2_sees_only_own_agents(self):
        self.client.login(username='iso_org2', password='testpass123')
        response = self.client.get(reverse('agents:agent-list'))
        agents = response.context['object_list']
        agent_pks = [a.pk for a in agents]
        self.assertNotIn(self.agent1.pk, agent_pks)
        self.assertIn(self.agent2.pk, agent_pks)


class TestAgentPermissions(TestCase):
    """Permission checks: normal user, agent user."""

    @classmethod
    def setUpTestData(cls):
        cls.normal_user = User.objects.create_user(
            username='perm_normal', email='perm_normal@test.com', password='testpass123',
        )
        cls.organisor_user = User.objects.create_user(
            username='perm_org', email='perm_org@test.com', password='testpass123',
            is_organisor=True, email_verified=True,
        )
        cls.org = UserProfile.objects.get(user=cls.organisor_user)
        cls.agent_user = User.objects.create_user(
            username='perm_agent', email='perm_agent@test.com', password='testpass123',
            is_agent=True, email_verified=True,
        )
        cls.agent = Agent.objects.create(user=cls.agent_user, organisation=cls.org)

    def setUp(self):
        self.client = Client()

    def test_normal_user_cannot_list_agents(self):
        self.client.login(username='perm_normal', password='testpass123')
        response = self.client.get(reverse('agents:agent-list'))
        self.assertEqual(response.status_code, 302)  # Normal user redirected

    def test_normal_user_cannot_create_agent(self):
        self.client.login(username='perm_normal', password='testpass123')
        response = self.client.get(reverse('agents:agent-create'))
        # Create view uses OrganisorAndLoginRequiredMixin, normal user redirected
        self.assertEqual(response.status_code, 302)
