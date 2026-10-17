"""Account delivery failures must not leave half-created accounts or uploads."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from google.auth.exceptions import RefreshError

from leads.models import Agent, UserProfile, EmailVerificationToken
from organisors.models import Organisor


class AccountDeliveryRegressionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.admin = User.objects.create_superuser('mail-admin', 'mail-admin@example.com', 'testpass123')
        cls.owner = User.objects.create_user(username='mail-owner', email='mail-owner@example.com', password='testpass123', email_verified=True)

    def setUp(self):
        self.media = TemporaryDirectory(prefix='crm-account-test-')
        self.addCleanup(self.media.cleanup)
        settings = override_settings(MEDIA_ROOT=self.media.name, EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
        settings.enable()
        self.addCleanup(settings.disable)

    def payload(self, key):
        return {'username': f'delivery-{key}', 'email': f'delivery-{key}@example.com', 'first_name': 'Delivery', 'last_name': 'Test', 'phone_number_0': '+1', 'phone_number_1': '2025550175', 'date_of_birth': '1990-01-01', 'gender': 'O', 'password1': 'TestDelivery!982', 'password2': 'TestDelivery!982', 'profile_image': SimpleUploadedFile('new-profile.jpg', b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xd9', content_type='image/jpeg')}

    def assert_failed_creation(self, url, key, actor=None):
        if actor:
            self.client.force_login(actor)
        counts = {model: model.objects.count() for model in [get_user_model(), UserProfile, Agent, Organisor, EmailVerificationToken]}
        error = RefreshError('invalid_grant: Token has been expired or revoked.', {'error': 'invalid_grant'})
        with patch('leads.services.django_send_mail', side_effect=error), self.assertLogs('leads.services', level='ERROR'):
            response = self.client.post(url, self.payload(key))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Email delivery is temporarily unavailable')
        self.assertNotContains(response, 'invalid_grant')
        for model, count in counts.items():
            self.assertEqual(model.objects.count(), count)
        self.assertEqual([p for p in Path(self.media.name).rglob('*') if p.is_file()], [])

    def test_signup_failure_rolls_back_account_token_and_photo(self):
        self.assert_failed_creation(reverse('signup'), 'signup')

    def test_organisor_invitation_failure_rolls_back_account_and_photo(self):
        self.assert_failed_creation(reverse('organisors:organisor-create'), 'org', self.admin)

    def test_agent_invitation_failure_rolls_back_account_and_photo(self):
        self.assert_failed_creation(reverse('agents:agent-create'), 'agent', self.owner)

    def test_signup_can_be_retried_after_delivery_failure(self):
        self.assert_failed_creation(reverse('signup'), 'retry')
        response = self.client.post(reverse('signup'), self.payload('retry'))
        self.assertRedirects(response, reverse('verify-email-sent'))
        user = get_user_model().objects.get(username='delivery-retry')
        self.assertFalse(user.email_verified)
        self.assertTrue(Organisor.objects.filter(user=user).exists())
        token = EmailVerificationToken.objects.get(user=user)
        self.assertEqual(len(mail.outbox), 1)
        self.client.get(reverse('verify-email', kwargs={'token': token.token}))
        user.refresh_from_db()
        self.assertTrue(user.email_verified)
        self.assertTrue(self.client.login(username=user.username, password='TestDelivery!982'))

    def test_password_reset_delivery_failure_is_a_form_error(self):
        with patch('django.core.mail.EmailMultiAlternatives.send', side_effect=RefreshError('invalid_grant')), self.assertLogs('leads.views', level='ERROR'):
            response = self.client.post(reverse('reset-password'), {'email': self.owner.email})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Email delivery is temporarily unavailable')
        self.owner.refresh_from_db()
        self.assertTrue(self.owner.check_password('testpass123'))

    def test_backend_returning_zero_is_treated_as_delivery_failure(self):
        with patch('leads.services.django_send_mail', return_value=0), self.assertLogs('leads.services', level='ERROR'):
            response = self.client.post(reverse('signup'), self.payload('zero'))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(get_user_model().objects.filter(username='delivery-zero').exists())
        self.assertEqual([p for p in Path(self.media.name).rglob('*') if p.is_file()], [])

    def reset_confirm_url(self):
        response = self.client.get(reverse('password_reset_confirm', kwargs={
            'uidb64': urlsafe_base64_encode(force_bytes(self.owner.pk)),
            'token': default_token_generator.make_token(self.owner),
        }))
        self.assertEqual(response.status_code, 302)
        return response.url

    def test_successful_reset_sends_confirmation_once_and_invalidates_link(self):
        url = self.reset_confirm_url()
        data = {'new_password1': 'ResetDelivery!982', 'new_password2': 'ResetDelivery!982'}
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse('password_reset_complete'))
        self.owner.refresh_from_db()
        self.assertTrue(self.owner.check_password(data['new_password1']))
        self.assertFalse(self.owner.check_password('testpass123'))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.owner.email])
        self.assertEqual(mail.outbox[0].subject, 'Darkenyas CRM - Password Reset Successful')
        self.client.get(reverse('password_reset_complete'))
        self.client.post(url, data)
        self.assertEqual(len(mail.outbox), 1)

    def test_mismatched_passwords_do_not_send_confirmation_or_change_password(self):
        response = self.client.post(self.reset_confirm_url(), {
            'new_password1': 'ResetDelivery!982', 'new_password2': 'DifferentDelivery!982',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)
        self.owner.refresh_from_db()
        self.assertTrue(self.owner.check_password('testpass123'))
        self.assertEqual(len(mail.outbox), 0)

    def test_confirmation_delivery_failure_keeps_successful_password_change(self):
        url = self.reset_confirm_url()
        with patch('leads.services.django_send_mail', side_effect=RefreshError('invalid_grant')), self.assertLogs('leads.services', level='ERROR'):
            response = self.client.post(url, {
                'new_password1': 'ResetDelivery!982', 'new_password2': 'ResetDelivery!982',
            }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [(reverse('password_reset_complete'), 302)])
        self.assertContains(response, 'Your password was changed, but the confirmation email could not be sent.')
        self.assertNotContains(response, 'invalid_grant')
        self.owner.refresh_from_db()
        self.assertTrue(self.owner.check_password('ResetDelivery!982'))
        self.assertTrue(self.client.login(username=self.owner.username, password='ResetDelivery!982'))

    def test_requesting_reset_does_not_send_success_confirmation(self):
        response = self.client.post(reverse('reset-password'), {'email': self.owner.email}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertNotEqual(mail.outbox[0].subject, 'Darkenyas CRM - Password Reset Successful')
