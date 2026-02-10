"""
Tests for organisors.models – Organisor model.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model

from organisors.models import Organisor
from leads.models import UserProfile

User = get_user_model()


class OrganisorModelTests(TestCase):
    """Tests for the Organisor model."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='orgmodel', email='orgmodel@test.com', password='testpass123',
            is_organisor=True, email_verified=True,
        )
        cls.organisation = UserProfile.objects.get(user=cls.user)
        cls.organisor = Organisor.objects.create(
            user=cls.user, organisation=cls.organisation,
        )

    def test_str_returns_user_email(self):
        self.assertEqual(str(self.organisor), 'orgmodel@test.com')

    def test_one_to_one_user_relationship(self):
        self.assertEqual(self.organisor.user, self.user)

    def test_organisation_fk(self):
        self.assertEqual(self.organisor.organisation, self.organisation)

    def test_cascade_delete_with_user(self):
        """Deleting the user cascades to the Organisor."""
        user = User.objects.create_user(
            username='delorg', email='delorg@test.com', password='testpass123',
            is_organisor=True,
        )
        org_profile = UserProfile.objects.get(user=user)
        Organisor.objects.create(user=user, organisation=org_profile)
        user_pk = user.pk
        user.delete()
        self.assertFalse(Organisor.objects.filter(user_id=user_pk).exists())
