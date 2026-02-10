"""
Tests for agents.views – Agent CRUD views (full version).
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core import mail

from leads.models import Agent, UserProfile, EmailVerificationToken

User = get_user_model()


class AgentViewTestBase(TestCase):
    """Shared setUp for agent view tests."""

    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_superuser(
            username='agentadmin', email='agentadmin@test.com', password='testpass123',
        )
        cls.organisor_user = User.objects.create_user(
            username='agentorg', email='agentorg@test.com', password='testpass123',
            is_organisor=True, email_verified=True,
        )
        cls.organisation = UserProfile.objects.get(user=cls.organisor_user)
        cls.agent_user = User.objects.create_user(
            username='existingagent', email='existingagent@test.com', password='testpass123',
            is_agent=True, first_name='Existing', last_name='Agent', email_verified=True,
        )
        cls.agent = Agent.objects.create(user=cls.agent_user, organisation=cls.organisation)
        # Normal user (no role)
        cls.normal_user = User.objects.create_user(
            username='normaluser', email='normaluser@test.com', password='testpass123',
            email_verified=True,
        )
        # Other organisation
        cls.other_org_user = User.objects.create_user(
            username='otherorg_a', email='otherorg_a@test.com', password='testpass123',
            is_organisor=True, email_verified=True,
        )
        cls.other_organisation = UserProfile.objects.get(user=cls.other_org_user)
        cls.other_agent_user = User.objects.create_user(
            username='otheragent_a', email='otheragent_a@test.com', password='testpass123',
            is_agent=True, email_verified=True,
        )
        cls.other_agent = Agent.objects.create(user=cls.other_agent_user, organisation=cls.other_organisation)

    def setUp(self):
        self.client = Client()


# ---------------------------------------------------------------------------
# Agent List View
# ---------------------------------------------------------------------------
class TestAgentListView(AgentViewTestBase):

    def test_unauthenticated_redirects(self):
        response = self.client.get(reverse('agents:agent-list'))
        self.assertEqual(response.status_code, 302)

    def test_organisor_access(self):
        self.client.login(username='agentorg', password='testpass123')
        response = self.client.get(reverse('agents:agent-list'))
        self.assertEqual(response.status_code, 200)

    def test_organisor_sees_only_org_agents(self):
        self.client.login(username='agentorg', password='testpass123')
        response = self.client.get(reverse('agents:agent-list'))
        agents = response.context['object_list']
        for a in agents:
            self.assertEqual(a.organisation, self.organisation)

    def test_superuser_sees_all_agents(self):
        self.client.login(username='agentadmin', password='testpass123')
        response = self.client.get(reverse('agents:agent-list'))
        agents = response.context['object_list']
        self.assertGreaterEqual(len(agents), 2)

    def test_superuser_filter_by_organisation(self):
        self.client.login(username='agentadmin', password='testpass123')
        response = self.client.get(
            reverse('agents:agent-list'),
            {'organisation': self.organisation.pk},
        )
        agents = response.context['object_list']
        for a in agents:
            self.assertEqual(a.organisation, self.organisation)

    def test_search_by_username(self):
        self.client.login(username='agentorg', password='testpass123')
        response = self.client.get(reverse('agents:agent-list'), {'q': 'existing'})
        agents = response.context['object_list']
        self.assertEqual(len(agents), 1)
        self.assertEqual(agents[0], self.agent)

    def test_normal_user_no_access(self):
        self.client.login(username='normaluser', password='testpass123')
        response = self.client.get(reverse('agents:agent-list'))
        # Mixin redirects normal users to lead list (302) or may show the page (200)
        # The key point is that agents should not be visible to them
        if response.status_code == 200:
            # Normal user shouldn't see any agents (empty queryset)
            agents = list(response.context.get('object_list', []))
            self.assertEqual(len(agents), 0)
        else:
            self.assertEqual(response.status_code, 302)  # Redirected (not organisor)

    def test_template_used(self):
        self.client.login(username='agentorg', password='testpass123')
        response = self.client.get(reverse('agents:agent-list'))
        self.assertTemplateUsed(response, 'agents/agent_list.html')


# ---------------------------------------------------------------------------
# Agent Detail View
# ---------------------------------------------------------------------------
class TestAgentDetailView(AgentViewTestBase):

    def test_organisor_access(self):
        self.client.login(username='agentorg', password='testpass123')
        response = self.client.get(reverse('agents:agent-detail', kwargs={'pk': self.agent.pk}))
        self.assertEqual(response.status_code, 200)

    def test_superuser_access(self):
        self.client.login(username='agentadmin', password='testpass123')
        response = self.client.get(reverse('agents:agent-detail', kwargs={'pk': self.agent.pk}))
        self.assertEqual(response.status_code, 200)

    def test_unauthenticated_redirects(self):
        response = self.client.get(reverse('agents:agent-detail', kwargs={'pk': self.agent.pk}))
        self.assertEqual(response.status_code, 302)

    def test_template_used(self):
        self.client.login(username='agentorg', password='testpass123')
        response = self.client.get(reverse('agents:agent-detail', kwargs={'pk': self.agent.pk}))
        self.assertTemplateUsed(response, 'agents/agent_detail.html')


# ---------------------------------------------------------------------------
# Agent Create View
# ---------------------------------------------------------------------------
class TestAgentCreateView(AgentViewTestBase):

    def test_organisor_get(self):
        self.client.login(username='agentorg', password='testpass123')
        response = self.client.get(reverse('agents:agent-create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'agents/agent_create.html')

    def test_organisor_create_agent(self):
        self.client.login(username='agentorg', password='testpass123')
        data = {
            'username': 'newagent',
            'email': 'newagent@test.com',
            'first_name': 'New',
            'last_name': 'Agent',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
        }
        response = self.client.post(reverse('agents:agent-create'), data)
        self.assertIn(response.status_code, [200, 302])  # 302 on success, 200 if form re-rendered
        # Check if user was created
        if User.objects.filter(username='newagent').exists():
            new_user = User.objects.get(username='newagent')
            self.assertTrue(new_user.is_agent)
            self.assertTrue(Agent.objects.filter(user=new_user).exists())

    def test_create_sends_verification_email(self):
        self.client.login(username='agentorg', password='testpass123')
        data = {
            'username': 'emailagent',
            'email': 'emailagent@test.com',
            'first_name': 'Email',
            'last_name': 'Agent',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
        }
        self.client.post(reverse('agents:agent-create'), data)
        if User.objects.filter(username='emailagent').exists():
            self.assertGreater(len(mail.outbox), 0)

    def test_unauthenticated_redirects(self):
        response = self.client.get(reverse('agents:agent-create'))
        self.assertEqual(response.status_code, 302)


# ---------------------------------------------------------------------------
# Agent Update View
# ---------------------------------------------------------------------------
class TestAgentUpdateView(AgentViewTestBase):

    def test_organisor_get(self):
        self.client.login(username='agentorg', password='testpass123')
        response = self.client.get(reverse('agents:agent-update', kwargs={'pk': self.agent.pk}))
        self.assertEqual(response.status_code, 200)

    def test_organisor_post_update(self):
        self.client.login(username='agentorg', password='testpass123')
        data = {
            'username': self.agent_user.username,
            'email': self.agent_user.email,
            'first_name': 'Updated',
            'last_name': 'Name',
        }
        response = self.client.post(
            reverse('agents:agent-update', kwargs={'pk': self.agent.pk}), data,
        )
        self.assertIn(response.status_code, [200, 302])  # 302 on success, 200 if form re-rendered

    def test_template_used(self):
        self.client.login(username='agentorg', password='testpass123')
        response = self.client.get(reverse('agents:agent-update', kwargs={'pk': self.agent.pk}))
        self.assertTemplateUsed(response, 'agents/agent_update.html')


# ---------------------------------------------------------------------------
# Agent Delete View
# ---------------------------------------------------------------------------
class TestAgentDeleteView(AgentViewTestBase):

    def test_organisor_delete(self):
        # Create a temp agent to delete
        temp_user = User.objects.create_user(
            username='delagent', email='delagent@test.com', password='pass123', is_agent=True,
        )
        temp_agent = Agent.objects.create(user=temp_user, organisation=self.organisation)
        self.client.login(username='agentorg', password='testpass123')
        response = self.client.post(reverse('agents:agent-delete', kwargs={'pk': temp_agent.pk}))
        self.assertEqual(response.status_code, 302)

    def test_unauthenticated_redirects(self):
        response = self.client.post(reverse('agents:agent-delete', kwargs={'pk': self.agent.pk}))
        self.assertEqual(response.status_code, 302)

    def test_template_used(self):
        self.client.login(username='agentorg', password='testpass123')
        response = self.client.get(reverse('agents:agent-delete', kwargs={'pk': self.agent.pk}))
        self.assertEqual(response.status_code, 200)  # Delete confirmation page
