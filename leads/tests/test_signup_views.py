"""
Signup Views Test File
This file tests all signup-related views.
"""

from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.core import mail
from django.utils import timezone
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from leads.models import User, UserProfile, EmailVerificationToken
from organisors.models import Organisor

User = get_user_model()

# Minimal valid JPEG bytes for magic-byte validation (imghdr.what)
VALID_JPEG_BYTES = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xd9'

SIMPLE_STATIC = {'STATICFILES_STORAGE': 'django.contrib.staticfiles.storage.StaticFilesStorage'}


@override_settings(**SIMPLE_STATIC)
class TestSignupView(TestCase):
    """SignupView tests"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        self.valid_data = {
            'username': 'testuser_signup_views',
            'email': 'test_signup_views@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'phone_number_0': '+90',
            'phone_number_1': '5551234567',
            'date_of_birth': '1990-01-01',
            'gender': 'M',
            'password1': 'testpass123!',
            'password2': 'testpass123!',
            'profile_image': SimpleUploadedFile("profile.jpg", VALID_JPEG_BYTES, content_type="image/jpeg"),
        }
    
    def test_signup_view_get(self):
        """Signup page GET request test"""
        response = self.client.get(reverse('signup'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sign Up')
        self.assertContains(response, 'form')
        # CSRF token should be in form
        self.assertContains(response, 'csrfmiddlewaretoken')
    
    @patch('leads.views.send_mail')
    def test_signup_view_post_valid_data(self, mock_send_mail):
        """Signup POST request valid data test"""
        response = self.client.post(reverse('signup'), self.valid_data, format='multipart')
        
        # Should redirect
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('verify-email-sent'))
        
        # Was user created
        self.assertTrue(User.objects.filter(username='testuser_signup_views').exists())
        
        user = User.objects.get(username='testuser_signup_views')
        
        # Are user attributes correct
        self.assertEqual(user.email, 'test_signup_views@example.com')
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User')
        self.assertEqual(user.phone_number, '+905551234567')
        self.assertEqual(user.gender, 'M')
        self.assertEqual(user.date_of_birth.strftime('%Y-%m-%d'), '1990-01-01')
        self.assertTrue(user.is_organisor)
        self.assertFalse(user.is_agent)
        self.assertFalse(user.email_verified)
        
        # Was UserProfile created
        self.assertTrue(UserProfile.objects.filter(user=user).exists())
        
        # Was Organisor created
        self.assertTrue(Organisor.objects.filter(user=user).exists())
        
        # Was email verification token created
        self.assertTrue(EmailVerificationToken.objects.filter(user=user).exists())
        
        # Was email sent
        mock_send_mail.assert_called_once()
    
    def test_signup_view_post_invalid_data(self):
        """Signup POST request invalid data test"""
        invalid_data = self.valid_data.copy()
        invalid_data['email'] = 'invalid-email'  # Invalid email
        
        response = self.client.post(reverse('signup'), invalid_data, format='multipart')
        
        # Returns with form errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
        
        # User was not created
        self.assertFalse(User.objects.filter(username='testuser_signup_views').exists())
    
    def test_signup_view_duplicate_email(self):
        """Duplicate email registration test"""
        # Create a user first
        User.objects.create_user(
            username='existing_user',
            email='existing@example.com',
            password='testpass123'
        )
        
        # Try to register with same email
        data = self.valid_data.copy()
        data['email'] = 'existing@example.com'
        data['username'] = 'different_username'
        
        response = self.client.post(reverse('signup'), data, format='multipart')
        
        # Returns with form errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
        
        # New user was not created
        self.assertFalse(User.objects.filter(username='different_username').exists())
    
    def test_signup_view_duplicate_username(self):
        """Duplicate username registration test"""
        # Create a user first
        User.objects.create_user(
            username='existing_user',
            email='existing@example.com',
            password='testpass123'
        )
        
        # Try to register with same username
        data = self.valid_data.copy()
        data['username'] = 'existing_user'
        data['email'] = 'different@example.com'
        
        response = self.client.post(reverse('signup'), data, format='multipart')
        
        # Returns with form errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
        
        # New user was not created
        self.assertFalse(User.objects.filter(email='different@example.com').exists())
    
    def test_signup_view_password_mismatch(self):
        """Password mismatch test"""
        data = self.valid_data.copy()
        data['password1'] = 'password123!'
        data['password2'] = 'differentpassword123!'
        
        response = self.client.post(reverse('signup'), data, format='multipart')
        
        # Returns with form errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
        
        # User was not created
        self.assertFalse(User.objects.filter(username='testuser_signup_views').exists())
    
    @patch('leads.views.send_mail')
    def test_signup_view_email_sending(self, mock_send_mail):
        """Email sending test"""
        response = self.client.post(reverse('signup'), self.valid_data, format='multipart')
        
        # Was email sent
        mock_send_mail.assert_called_once()
        
        # Is email content correct
        call_args = mock_send_mail.call_args
        # send_mail positional args: subject, message, from_email, recipient_list
        self.assertEqual(call_args[0][0], 'Darkenyas CRM - Email Verification')  # subject
        self.assertIn('test_signup_views@example.com', call_args[0][3])  # recipient_list
        self.assertIn('Test', call_args[0][1])  # message - First name
        self.assertIn('verify-email', call_args[0][1])  # message - Verification link
    
    def test_signup_view_template(self):
        """Template test"""
        response = self.client.get(reverse('signup'))
        
        self.assertTemplateUsed(response, 'registration/signup.html')
        self.assertContains(response, 'Sign Up')
        self.assertContains(response, 'Create your account')
        self.assertContains(response, 'Already have an account?')
    
    def test_signup_view_form_class(self):
        """Form class test"""
        response = self.client.get(reverse('signup'))
        
        self.assertIn('form', response.context)
        from leads.forms import CustomUserCreationForm
        self.assertIsInstance(response.context['form'], CustomUserCreationForm)
    
    def test_signup_view_success_url(self):
        """Success URL test"""
        with patch('leads.views.send_mail'):
            response = self.client.post(reverse('signup'), self.valid_data, format='multipart')
            self.assertRedirects(response, reverse('verify-email-sent'))


@override_settings(**SIMPLE_STATIC)
class TestEmailVerificationSentView(TestCase):
    """EmailVerificationSentView tests"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
    
    def test_email_verification_sent_view_get(self):
        """Email verification sent page GET request test"""
        response = self.client.get(reverse('verify-email-sent'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/verify_email_sent.html')
    
    def test_email_verification_sent_view_content(self):
        """Email verification sent page content test"""
        response = self.client.get(reverse('verify-email-sent'))
        
        self.assertContains(response, 'verification')
        self.assertContains(response, 'email')


@override_settings(**SIMPLE_STATIC)
class TestEmailVerificationView(TestCase):
    """EmailVerificationView tests"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create test user
        self.user = User.objects.create_user(
            username='verification_test_user',
            email='verification_test@example.com',
            password='testpass123',
            first_name='Verification',
            last_name='Test',
            is_organisor=True,
            email_verified=False
        )
        
        # Create email verification token
        self.verification_token = EmailVerificationToken.objects.create(
            user=self.user
        )
    
    def test_email_verification_valid_token(self):
        """Email verification with valid token test"""
        response = self.client.get(
            reverse('verify-email', kwargs={'token': self.verification_token.token})
        )
        
        # Should redirect to verification success page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('verify-email-success'))
        
        # Was user email verified
        updated_user = User.objects.get(pk=self.user.pk)
        self.assertTrue(updated_user.email_verified)
        
        # Was token marked as used
        updated_token = EmailVerificationToken.objects.get(pk=self.verification_token.pk)
        self.assertTrue(updated_token.is_used)
    
    def test_email_verification_invalid_token(self):
        """Email verification with invalid token test"""
        fake_token = '00000000-0000-0000-0000-000000000000'
        
        response = self.client.get(
            reverse('verify-email', kwargs={'token': fake_token})
        )
        
        # Should redirect to verification failed page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('verify-email-failed'))
        
        # User email was not verified
        updated_user = User.objects.get(pk=self.user.pk)
        self.assertFalse(updated_user.email_verified)
    
    def test_email_verification_used_token(self):
        """Email verification with used token test"""
        # Mark token as used
        self.verification_token.is_used = True
        self.verification_token.save()
        
        response = self.client.get(
            reverse('verify-email', kwargs={'token': self.verification_token.token})
        )
        
        # Should redirect to verification failed page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('verify-email-failed'))
        
        # User email was not verified
        updated_user = User.objects.get(pk=self.user.pk)
        self.assertFalse(updated_user.email_verified)
    
    def test_email_verification_expired_token(self):
        """Email verification with expired token test"""
        # Create token 25 hours ago (24-hour window expired)
        expired_time = timezone.now() - timedelta(hours=25)
        self.verification_token.created_at = expired_time
        self.verification_token.save()
        
        response = self.client.get(
            reverse('verify-email', kwargs={'token': self.verification_token.token})
        )
        
        # Should redirect to verification failed page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('verify-email-failed'))
        
        # User email was not verified
        updated_user = User.objects.get(pk=self.user.pk)
        self.assertFalse(updated_user.email_verified)
    
    def test_email_verification_already_verified(self):
        """Already verified email test"""
        # Mark user as already verified
        self.user.email_verified = True
        self.user.save()
        
        response = self.client.get(
            reverse('verify-email', kwargs={'token': self.verification_token.token})
        )
        
        # Verification should still complete (token marked as used)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('verify-email-success'))
        
        # Was token marked as used
        updated_token = EmailVerificationToken.objects.get(pk=self.verification_token.pk)
        self.assertTrue(updated_token.is_used)


@override_settings(**SIMPLE_STATIC)
class TestEmailVerificationFailedView(TestCase):
    """EmailVerificationFailedView tests"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
    
    def test_email_verification_failed_view_get(self):
        """Email verification failed page GET request test"""
        response = self.client.get(reverse('verify-email-failed'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/verify_email_failed.html')
    
    def test_email_verification_failed_view_content(self):
        """Email verification failed page content test"""
        response = self.client.get(reverse('verify-email-failed'))
        
        self.assertContains(response, 'verification')
        # Check template content
        self.assertContains(response, 'verification')


@override_settings(**SIMPLE_STATIC)
class TestSignupIntegration(TestCase):
    """Signup integration tests"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        self.valid_data = {
            'username': 'integration_test_user',
            'email': 'integration_test@example.com',
            'first_name': 'Integration',
            'last_name': 'Test',
            'phone_number_0': '+90',
            'phone_number_1': '5559876543',
            'date_of_birth': '1985-05-15',
            'gender': 'F',
            'password1': 'testpass123!',
            'password2': 'testpass123!',
            'profile_image': SimpleUploadedFile("profile.jpg", VALID_JPEG_BYTES, content_type="image/jpeg"),
        }
    
    @patch('leads.views.send_mail')
    def test_complete_signup_flow(self, mock_send_mail):
        """Complete signup flow test"""
        # 1. Go to signup page
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        
        # 2. Submit form
        response = self.client.post(reverse('signup'), self.valid_data, format='multipart')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('verify-email-sent'))
        
        # 3. Go to email verification sent page
        response = self.client.get(reverse('verify-email-sent'))
        self.assertEqual(response.status_code, 200)
        
        # 4. Check if user was created
        user = User.objects.get(username='integration_test_user')
        self.assertFalse(user.email_verified)
        
        # 5. Was email verification token created
        verification_token = EmailVerificationToken.objects.get(user=user)
        self.assertFalse(verification_token.is_used)
        
        # 6. Click email verification link
        response = self.client.get(
            reverse('verify-email', kwargs={'token': verification_token.token})
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('verify-email-success'))
        
        # 7. Was user email verified
        updated_user = User.objects.get(pk=user.pk)
        self.assertTrue(updated_user.email_verified)
        
        # 8. Was token marked as used
        updated_token = EmailVerificationToken.objects.get(pk=verification_token.pk)
        self.assertTrue(updated_token.is_used)
        
        # 9. Was email sent
        mock_send_mail.assert_called_once()
    
    def test_signup_with_duplicate_data(self):
        """Signup with conflicting data test"""
        # Create a user first
        User.objects.create_user(
            username='duplicate_user',
            email='duplicate@example.com',
            password='testpass123',
            phone_number='+905551111111'
        )
        
        # Try to sign up with same email
        data = self.valid_data.copy()
        data['email'] = 'duplicate@example.com'
        
        response = self.client.post(reverse('signup'), data, format='multipart')
        self.assertEqual(response.status_code, 200)  # Returns with form errors
        self.assertFalse(User.objects.filter(username='integration_test_user').exists())
        
        # Try to sign up with same phone number
        data = self.valid_data.copy()
        data['phone_number_0'] = '+90'
        data['phone_number_1'] = '5551111111'
        
        response = self.client.post(reverse('signup'), data, format='multipart')
        self.assertEqual(response.status_code, 200)  # Returns with form errors
        self.assertFalse(User.objects.filter(username='integration_test_user').exists())
    
    def test_signup_form_validation(self):
        """Signup form validation test"""
        # Missing fields
        incomplete_data = {
            'username': 'test_user',
            'email': 'test@example.com',
            # Other fields missing
        }
        
        response = self.client.post(reverse('signup'), incomplete_data, format='multipart')
        self.assertEqual(response.status_code, 200)  # Returns with form errors
        self.assertFalse(User.objects.filter(username='test_user').exists())
        
        # Invalid email format
        invalid_email_data = self.valid_data.copy()
        invalid_email_data['email'] = 'invalid-email-format'
        
        response = self.client.post(reverse('signup'), invalid_email_data, format='multipart')
        self.assertEqual(response.status_code, 200)  # Returns with form errors
        self.assertFalse(User.objects.filter(username='integration_test_user').exists())
        
        # Password mismatch
        password_mismatch_data = self.valid_data.copy()
        password_mismatch_data['password1'] = 'password123!'
        password_mismatch_data['password2'] = 'differentpassword123!'
        
        response = self.client.post(reverse('signup'), password_mismatch_data, format='multipart')
        self.assertEqual(response.status_code, 200)  # Returns with form errors
        self.assertFalse(User.objects.filter(username='integration_test_user').exists())


@override_settings(**SIMPLE_STATIC)
class TestEmailVerificationSuccessView(TestCase):
    """EmailVerificationSuccessView tests"""

    def setUp(self):
        self.client = Client()
        self.url = reverse('verify-email-success')

    def test_get_returns_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'registration/verify_email_success.html')
