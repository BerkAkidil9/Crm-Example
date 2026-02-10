# agents/tests/test_forms.py
from io import BytesIO

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model

from agents.forms import (
    AgentModelForm,
    AdminAgentModelForm,
    OrganisorAgentModelForm,
    AgentCreateForm,
    OrganisorAgentCreateForm,
    AdminAgentCreateForm,
)
from leads.models import UserProfile, Agent

User = get_user_model()

# Valid agent data - PhoneNumberWidget is a MultiWidget so we need _0 (country) and _1 (number)
VALID_AGENT_DATA = {
    'email': 'agentform@test.com',
    'username': 'agentform',
    'first_name': 'Agent',
    'last_name': 'Form',
    'phone_number_0': '+90',
    'phone_number_1': '5551111111',
    'date_of_birth': '1990-01-01',
    'gender': 'M',
}


class AgentModelFormTests(TestCase):
    """Tests for AgentModelForm (agent self-profile update)."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='existingagent',
            email='existingagent@test.com',
            password='testpass123',
            is_agent=True,
            email_verified=True,
            phone_number='+905552222221',
            date_of_birth='1985-05-15',
            gender='F',
            first_name='Existing',
            last_name='Agent',
        )

    def test_form_has_expected_fields(self):
        form = AgentModelForm(instance=self.user)
        self.assertIn('email', form.fields)
        self.assertIn('username', form.fields)
        self.assertIn('password1', form.fields)
        self.assertIn('password2', form.fields)
        self.assertFalse(form.fields['password1'].required)
        self.assertFalse(form.fields['password2'].required)

    def test_form_valid_without_password_change(self):
        form = AgentModelForm(instance=self.user, data={
            **VALID_AGENT_DATA,
            'email': 'existingagent@test.com',
            'username': 'existingagent',
            'phone_number_0': '+90',
            'phone_number_1': '5552222221',
        })
        self.assertTrue(form.is_valid(), form.errors)

    def test_form_invalid_duplicate_email(self):
        User.objects.create_user(
            username='otheruser',
            email='other@test.com',
            password='pass',
            phone_number='+905552222223',
            date_of_birth='1990-01-01',
            gender='M',
        )
        form = AgentModelForm(instance=self.user, data={
            **VALID_AGENT_DATA,
            'email': 'other@test.com',
            'username': 'existingagent',
            'phone_number_0': '+90',
            'phone_number_1': '5552222221',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_form_valid_password_change(self):
        form = AgentModelForm(instance=self.user, data={
            **VALID_AGENT_DATA,
            'email': 'existingagent@test.com',
            'username': 'existingagent',
            'phone_number_0': '+90',
            'phone_number_1': '5552222221',
            'password1': 'NewSecurePass123!',
            'password2': 'NewSecurePass123!',
        })
        self.assertTrue(form.is_valid(), form.errors)

    def test_form_invalid_password_mismatch(self):
        form = AgentModelForm(instance=self.user, data={
            **VALID_AGENT_DATA,
            'email': 'existingagent@test.com',
            'username': 'existingagent',
            'phone_number_0': '+90',
            'phone_number_1': '5552222221',
            'password1': 'NewSecurePass123!',
            'password2': 'DifferentPass123!',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)


class AdminAgentModelFormTests(TestCase):
    """Tests for AdminAgentModelForm (admin updates agent, with organisation)."""

    def setUp(self):
        self.org_user = User.objects.create_user(
            username='orgforadmin',
            email='orgforadmin@test.com',
            password='testpass123',
            is_organisor=True,
            email_verified=True,
            phone_number='+905553333331',
            date_of_birth='1990-01-01',
            gender='M',
        )
        self.org_profile = UserProfile.objects.get(user=self.org_user)
        self.agent_user = User.objects.create_user(
            username='agentforadmin',
            email='agentforadmin@test.com',
            password='testpass123',
            is_agent=True,
            email_verified=True,
            phone_number='+905553333332',
            date_of_birth='1992-01-01',
            gender='M',
            first_name='Agent',
            last_name='User',
        )
        self.agent = Agent.objects.create(
            user=self.agent_user,
            organisation=self.org_profile,
        )

    def test_form_has_organisation_field(self):
        form = AdminAgentModelForm(agent=self.agent, instance=self.agent_user)
        self.assertIn('organisation', form.fields)
        self.assertTrue(form.fields['organisation'].required)
        self.assertEqual(form.fields['organisation'].initial, self.org_profile)

    def test_form_valid(self):
        form = AdminAgentModelForm(
            agent=self.agent,
            instance=self.agent_user,
            data={
                'email': 'agentforadmin@test.com',
                'username': 'agentforadmin',
                'first_name': 'Agent',
                'last_name': 'User',
                'phone_number_0': '+90',
                'phone_number_1': '5553333332',
                'date_of_birth': '1992-01-01',
                'gender': 'M',
                'organisation': self.org_profile.pk,
            },
        )
        self.assertTrue(form.is_valid(), form.errors)


class OrganisorAgentModelFormTests(TestCase):
    """Tests for OrganisorAgentModelForm (organisor updates agent)."""

    def setUp(self):
        self.org_user = User.objects.create_user(
            username='orgforform',
            email='orgforform@test.com',
            password='testpass123',
            is_organisor=True,
            email_verified=True,
            phone_number='+905554444441',
            date_of_birth='1990-01-01',
            gender='M',
        )
        self.org_profile = UserProfile.objects.get(user=self.org_user)
        self.agent_user = User.objects.create_user(
            username='agentforform',
            email='agentforform@test.com',
            password='testpass123',
            is_agent=True,
            email_verified=True,
            phone_number='+905554444442',
            date_of_birth='1992-01-01',
            gender='M',
            first_name='A',
            last_name='B',
        )
        Agent.objects.create(user=self.agent_user, organisation=self.org_profile)

    def test_form_valid(self):
        form = OrganisorAgentModelForm(instance=self.agent_user, data={
            'email': 'agentforform@test.com',
            'username': 'agentforform',
            'first_name': 'A',
            'last_name': 'B',
            'phone_number_0': '+90',
            'phone_number_1': '5554444442',
            'date_of_birth': '1992-01-01',
            'gender': 'M',
        })
        self.assertTrue(form.is_valid(), form.errors)


class AgentCreateFormTests(TestCase):
    """Tests for AgentCreateForm (agent self-registration)."""

    def test_form_valid_creates_user(self):
        form = AgentCreateForm(data={
            **VALID_AGENT_DATA,
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
        })
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertEqual(user.email, VALID_AGENT_DATA['email'])
        self.assertTrue(user.check_password('SecurePass123!'))

    def test_form_invalid_duplicate_email(self):
        User.objects.create_user(
            username='taken',
            email='agentform@test.com',
            password='pass',
            phone_number='+905555555551',
            date_of_birth='1990-01-01',
            gender='M',
        )
        form = AgentCreateForm(data={
            **VALID_AGENT_DATA,
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_form_invalid_password_too_short(self):
        form = AgentCreateForm(data={
            **VALID_AGENT_DATA,
            'password1': 'short',
            'password2': 'short',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('password1', form.errors)

    def test_form_invalid_password_mismatch(self):
        form = AgentCreateForm(data={
            **VALID_AGENT_DATA,
            'password1': 'SecurePass123!',
            'password2': 'OtherPass123!',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)


class OrganisorAgentCreateFormTests(TestCase):
    """Tests for OrganisorAgentCreateForm (organisor creates agent, profile_image required)."""

    def test_form_has_profile_image_required(self):
        form = OrganisorAgentCreateForm()
        self.assertTrue(form.fields['profile_image'].required)

    def test_form_valid_with_image(self):
        image = SimpleUploadedFile(
            'test.jpg',
            b'fake image content',
            content_type='image/jpeg',
        )
        form = OrganisorAgentCreateForm(
            data={
                **VALID_AGENT_DATA,
                'username': 'orgcreateagent',
                'email': 'orgcreateagent@test.com',
                'phone_number_0': '+90',
                'phone_number_1': '5556666661',
                'password1': 'SecurePass123!',
                'password2': 'SecurePass123!',
            },
            files={'profile_image': image},
        )
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertEqual(user.username, 'orgcreateagent')

    def test_form_invalid_without_image(self):
        form = OrganisorAgentCreateForm(data={
            **VALID_AGENT_DATA,
            'username': 'noimage',
            'email': 'noimage@test.com',
            'phone_number_0': '+90',
            'phone_number_1': '5556666662',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('profile_image', form.errors)


class AdminAgentCreateFormTests(TestCase):
    """Tests for AdminAgentCreateForm (admin creates agent with organisation)."""

    def setUp(self):
        self.org_user = User.objects.create_user(
            username='orgforadmincreate',
            email='orgforadmincreate@test.com',
            password='testpass123',
            is_organisor=True,
            email_verified=True,
            phone_number='+905557777771',
            date_of_birth='1990-01-01',
            gender='M',
        )
        self.org_profile = UserProfile.objects.get(user=self.org_user)

    def test_form_has_organisation_required(self):
        form = AdminAgentCreateForm()
        self.assertIn('organisation', form.fields)
        self.assertTrue(form.fields['organisation'].required)

    def test_form_valid_with_organisation_and_image(self):
        image = SimpleUploadedFile(
            'admin_agent.jpg',
            b'fake image',
            content_type='image/jpeg',
        )
        form = AdminAgentCreateForm(
            data={
                **VALID_AGENT_DATA,
                'username': 'admincreateagent',
                'email': 'admincreateagent@test.com',
                'phone_number_0': '+90',
                'phone_number_1': '5557777772',
                'organisation': self.org_profile.pk,
                'password1': 'SecurePass123!',
                'password2': 'SecurePass123!',
            },
            files={'profile_image': image},
        )
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertEqual(user.username, 'admincreateagent')

    def test_form_invalid_organisation_required(self):
        image = SimpleUploadedFile(
            'x.jpg',
            b'x',
            content_type='image/jpeg',
        )
        form = AdminAgentCreateForm(
            data={
                **VALID_AGENT_DATA,
                'username': 'noorg',
                'email': 'noorg@test.com',
                'phone_number_0': '+90',
                'phone_number_1': '5557777773',
                'password1': 'SecurePass123!',
                'password2': 'SecurePass123!',
            },
            files={'profile_image': image},
        )
        self.assertFalse(form.is_valid())
        self.assertIn('organisation', form.errors)
