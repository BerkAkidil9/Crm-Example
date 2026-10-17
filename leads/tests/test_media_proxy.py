"""Protected media must recheck access and must not be cached publicly."""
from tempfile import TemporaryDirectory
from urllib.parse import urlsplit

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.test import TestCase, override_settings
from django.urls import reverse

from leads.models import Agent, Lead


class ProtectedMediaTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.admin = User.objects.create_superuser('media-admin', 'media-admin@example.com', 'testpass123')
        cls.owner = User.objects.create_user(username='media-owner', email='media-owner@example.com', email_verified=True)
        cls.other_owner = User.objects.create_user(username='media-other', email='media-other@example.com', email_verified=True)
        cls.agent_user = User.objects.create_user(username='media-agent', email='media-agent@example.com', is_agent=True, is_organisor=False, email_verified=True)
        cls.unassigned_user = User.objects.create_user(username='media-unassigned', email='media-unassigned@example.com', is_agent=True, is_organisor=False, email_verified=True)
        cls.agent = Agent.objects.create(user=cls.agent_user, organisation=cls.owner.userprofile)
        Agent.objects.create(user=cls.unassigned_user, organisation=cls.owner.userprofile)
        cls.lead_path = 'lead_photos/protected.jpg'
        cls.profile_path = 'profile_images/protected.jpg'
        cls.lead = Lead.objects.create(
            first_name='Media', last_name='Lead', organisation=cls.owner.userprofile,
            agent=cls.agent, profile_image=cls.lead_path,
            email='media-lead@example.com', phone_number='2025550197',
        )
        cls.agent_user.profile_image = cls.profile_path
        cls.agent_user.save(update_fields=['profile_image'])

    def setUp(self):
        media = TemporaryDirectory(prefix='crm-protected-media-')
        self.addCleanup(media.cleanup)
        settings = override_settings(MEDIA_ROOT=media.name, STORAGES={
            'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
            'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
        })
        settings.enable()
        self.addCleanup(settings.disable)
        for path in [self.lead_path, self.profile_path]:
            default_storage.save(path, ContentFile(b'private test image'))

    def get_image(self, path):
        return self.client.get(reverse('media-proxy', kwargs={'path': path}))

    def assert_uncached(self, response):
        directives = {part.strip() for part in response['Cache-Control'].split(',')}
        self.assertTrue({'private', 'no-store', 'no-cache', 'max-age=0', 'must-revalidate'} <= directives)
        self.assertNotIn('public', directives)
        self.assertIn('cookie', response['Vary'].lower())

    def test_authorised_media_is_served_with_private_no_store_headers(self):
        for user in [self.admin, self.owner, self.agent_user]:
            self.client.force_login(user)
            for path in [self.lead_path, self.profile_path]:
                with self.subTest(user=user.username, path=path):
                    response = self.get_image(path)
                    self.assertEqual(response.status_code, 200)
                    self.assert_uncached(response)
                    self.assertEqual(b''.join(response.streaming_content), b'private test image')
                    response.close()

    def test_other_organisation_and_unassigned_agent_cannot_reuse_media(self):
        self.client.force_login(self.owner)
        response = self.get_image(self.lead_path)
        self.assertEqual(response.status_code, 200)
        response.close()
        for user in [self.other_owner, self.unassigned_user]:
            self.client.force_login(user)
            for path in [self.lead_path, self.profile_path]:
                self.assertEqual(self.get_image(path).status_code, 404)

    def test_anonymous_requests_redirect_to_login_without_caching(self):
        for path in [self.lead_path, self.profile_path]:
            response = self.get_image(path)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(urlsplit(response.url).path.rstrip('/'), reverse('login').rstrip('/'))
            self.assert_uncached(response)

    def test_missing_unknown_and_traversal_paths_are_denied(self):
        self.client.force_login(self.admin)
        for path in ['lead_photos/missing.jpg', 'other/protected.jpg', '../profile_images/protected.jpg']:
            self.assertEqual(self.get_image(path).status_code, 404)

    def test_non_get_requests_are_rejected_without_caching(self):
        self.client.force_login(self.owner)
        response = self.client.post(reverse('media-proxy', kwargs={'path': self.lead_path}))
        self.assertEqual(response.status_code, 405)
        self.assert_uncached(response)
