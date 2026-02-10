"""
Tests for organisors.views – Organisor CRUD views access control.
"""
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model

from organisors.models import Organisor
from leads.models import UserProfile

User = get_user_model()

SIMPLE_STATIC = {
    'STATICFILES_STORAGE': 'django.contrib.staticfiles.storage.StaticFilesStorage',
}


@override_settings(**SIMPLE_STATIC)
class OrganisorViewAccessTests(TestCase):
    """Basic access control tests for organisor views."""

    @classmethod
    def setUpTestData(cls):
        # Admin user
        cls.admin = User.objects.create_superuser(
            username='orgviewadmin', email='orgviewadmin@test.com', password='testpass123',
        )
        # Organisor user
        cls.org_user = User.objects.create_user(
            username='orgvieworg', email='orgvieworg@test.com', password='testpass123',
            is_organisor=True, email_verified=True,
        )
        cls.organisation = UserProfile.objects.get(user=cls.org_user)
        cls.organisor = Organisor.objects.create(
            user=cls.org_user, organisation=cls.organisation,
        )

    def setUp(self):
        self.client = Client()

    # -- anonymous --
    def test_list_anonymous_redirected(self):
        response = self.client.get(reverse('organisors:organisor-list'))
        self.assertEqual(response.status_code, 302)

    # -- admin CRUD --
    def test_admin_can_list(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('organisors:organisor-list'))
        self.assertEqual(response.status_code, 200)

    def test_admin_can_view_detail(self):
        self.client.force_login(self.admin)
        response = self.client.get(
            reverse('organisors:organisor-detail', kwargs={'pk': self.organisor.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_admin_can_access_create(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('organisors:organisor-create'))
        self.assertEqual(response.status_code, 200)

    def test_list_uses_correct_template(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('organisors:organisor-list'))
        self.assertTemplateUsed(response, 'organisors/organisor_list.html')
