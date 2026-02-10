"""
Login Views Test File
This file tests all views related to login.
"""

from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.utils import timezone
from unittest.mock import patch, MagicMock

from leads.models import User, UserProfile, EmailVerificationToken
from organisors.models import Organisor

User = get_user_model()

SIMPLE_STATIC = {'STATICFILES_STORAGE': 'django.contrib.staticfiles.storage.StaticFilesStorage'}


@override_settings(**SIMPLE_STATIC)
class TestCustomLoginView(TestCase):
    """CustomLoginView tests"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create test user (email verified)
        self.user = User.objects.create_user(
            username='testuser_login_views',
            email='test_login_views@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            phone_number='+905551234567',
            date_of_birth='1990-01-01',
            gender='M',
            is_organisor=True,
            email_verified=True
        )
        
        # Create UserProfile
        self.user_profile, created = UserProfile.objects.get_or_create(user=self.user)
        
        # Create Organisor
        Organisor.objects.create(user=self.user, organisation=self.user_profile)
        
        # Unverified email user
        self.unverified_user = User.objects.create_user(
            username='unverified_user',
            email='unverified@example.com',
            password='testpass123',
            first_name='Unverified',
            last_name='User',
            phone_number='+905559876543',
            date_of_birth='1985-05-15',
            gender='F',
            is_organisor=True,
            email_verified=False
        )
        
        # Create UserProfile
        self.unverified_user_profile, created = UserProfile.objects.get_or_create(user=self.unverified_user)
        
        # Create Organisor
        Organisor.objects.create(user=self.unverified_user, organisation=self.unverified_user_profile)
    
    def test_login_view_get(self):
        """Login page GET request test"""
        response = self.client.get(reverse('login'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')
        self.assertContains(response, 'Welcome back!')
        self.assertContains(response, 'form')
        # CSRF token should be in form
        self.assertContains(response, 'csrfmiddlewaretoken')
    
    def test_login_view_post_valid_username(self):
        """Login POST request test with valid username"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser_login_views',
            'password': 'testpass123'
        })
        
        # Should redirect
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('landing-page'))
        
        # Is user logged in
        self.assertTrue(self.client.session.get('_auth_user_id'))
    
    def test_login_view_post_valid_email(self):
        """Login POST request test with valid email"""
        response = self.client.post(reverse('login'), {
            'username': 'test_login_views@example.com',
            'password': 'testpass123'
        })
        
        # Should redirect
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('landing-page'))
        
        # Is user logged in
        self.assertTrue(self.client.session.get('_auth_user_id'))
    
    def test_login_view_post_invalid_credentials(self):
        """Login POST request test with invalid credentials"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser_login_views',
            'password': 'wrongpassword'
        })
        
        # Returns with form errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
        
        # User should not be logged in
        self.assertFalse(self.client.session.get('_auth_user_id'))
    
    def test_login_view_post_unverified_email(self):
        """Login test with unverified email user"""
        response = self.client.post(reverse('login'), {
            'username': 'unverified_user',
            'password': 'testpass123'
        })
        
        # Returns with form errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
        
        # User should not be logged in
        self.assertFalse(self.client.session.get('_auth_user_id'))
    
    def test_login_view_post_nonexistent_user(self):
        """Login test with non-existent user"""
        response = self.client.post(reverse('login'), {
            'username': 'nonexistent_user',
            'password': 'testpass123'
        })
        
        # Returns with form errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
        
        # User should not be logged in
        self.assertFalse(self.client.session.get('_auth_user_id'))
    
    def test_login_view_post_empty_credentials(self):
        """Login test with empty credentials"""
        response = self.client.post(reverse('login'), {
            'username': '',
            'password': ''
        })
        
        # Returns with form errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
        
        # User should not be logged in
        self.assertFalse(self.client.session.get('_auth_user_id'))
    
    def test_login_view_template(self):
        """Template test"""
        response = self.client.get(reverse('login'))
        
        self.assertTemplateUsed(response, 'registration/login.html')
        self.assertContains(response, 'Login')
        self.assertContains(response, 'Welcome back!')
        self.assertContains(response, 'Username or Email')
        self.assertContains(response, 'Password')
        self.assertContains(response, 'Forget password?')
        self.assertContains(response, 'Don\'t have an account?')
    
    def test_login_view_form_class(self):
        """Form class test"""
        response = self.client.get(reverse('login'))
        
        self.assertIn('form', response.context)
        from leads.forms import CustomAuthenticationForm
        self.assertIsInstance(response.context['form'], CustomAuthenticationForm)
    
    def test_login_view_redirect_authenticated_user(self):
        """Redirect test for logged-in user"""
        # Log in first
        self.client.login(username='testuser_login_views', password='testpass123')
        
        # Go to login page
        response = self.client.get(reverse('login'))
        
        # Authenticated user is redirected (redirect_authenticated_user=True)
        self.assertEqual(response.status_code, 302)
    
    def test_login_view_success_redirect(self):
        """Successful login redirect test"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser_login_views',
            'password': 'testpass123'
        })
        
        # Should redirect to landing page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('landing-page'))
    
    def test_login_view_form_validation(self):
        """Form validation test"""
        # Invalid email format
        response = self.client.post(reverse('login'), {
            'username': 'invalid-email-format',
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
        
        # Username too long
        response = self.client.post(reverse('login'), {
            'username': 'a' * 300,  # Username too long
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
    
    def test_login_view_csrf_protection(self):
        """CSRF protection test"""
        # Django test client bypasses CSRF by default
        response = self.client.post(reverse('login'), {
            'username': 'testuser_login_views',
            'password': 'testpass123'
        }, follow=False)
        
        # Test client bypasses CSRF - successful login redirects
        self.assertEqual(response.status_code, 302)
    
    def test_login_view_remember_me_functionality(self):
        """Remember me functionality test (if implemented)"""
        # This test can be updated if remember me feature is added
        response = self.client.post(reverse('login'), {
            'username': 'testuser_login_views',
            'password': 'testpass123'
        })
        
        # Normal login test
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('landing-page'))
    
    def test_login_view_case_insensitive_username(self):
        """Case insensitive username test"""
        response = self.client.post(reverse('login'), {
            'username': 'TESTUSER_LOGIN_VIEWS',  # Uppercase
            'password': 'testpass123'
        })
        
        # Should redirect
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('landing-page'))
    
    def test_login_view_case_insensitive_email(self):
        """Case insensitive email test"""
        response = self.client.post(reverse('login'), {
            'username': 'TEST_LOGIN_VIEWS@EXAMPLE.COM',  # Uppercase
            'password': 'testpass123'
        })
        
        # Should redirect
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('landing-page'))
    
    def test_login_view_whitespace_handling(self):
        """Whitespace handling test"""
        response = self.client.post(reverse('login'), {
            'username': '  testuser_login_views  ',  # Leading and trailing whitespace
            'password': 'testpass123'
        })
        
        # Should redirect (whitespace trim edilmeli)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('landing-page'))


@override_settings(**SIMPLE_STATIC)
class TestLoginViewIntegration(TestCase):
    """Login view integration tests"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create test user
        self.user = User.objects.create_user(
            username='integration_test_user',
            email='integration_test@example.com',
            password='testpass123',
            first_name='Integration',
            last_name='Test',
            phone_number='+905559876543',
            date_of_birth='1985-05-15',
            gender='F',
            is_organisor=True,
            email_verified=True
        )
        
        # Create UserProfile
        self.user_profile, created = UserProfile.objects.get_or_create(user=self.user)
        
        # Create Organisor
        Organisor.objects.create(user=self.user, organisation=self.user_profile)
    
    def test_complete_login_flow(self):
        """Complete login flow test"""
        # 1. Go to login page
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        
        # 2. Submit login form
        response = self.client.post(reverse('login'), {
            'username': 'integration_test_user',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('landing-page'))
        
        # 3. Check if user is logged in
        self.assertTrue(self.client.session.get('_auth_user_id'))
        
        # 4. Protected page access test
        response = self.client.get(reverse('leads:lead-list'))
        self.assertEqual(response.status_code, 200)
    
    def test_login_with_different_credentials_formats(self):
        """Login test with different credential formats"""
        # With username
        self.client.logout()
        response = self.client.post(reverse('login'), {
            'username': 'integration_test_user',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)
        
        # With email
        self.client.logout()
        response = self.client.post(reverse('login'), {
            'username': 'integration_test@example.com',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)
    
    def test_login_after_logout(self):
        """Login test after logout"""
        # Log in first
        self.client.login(username='integration_test_user', password='testpass123')
        self.assertTrue(self.client.session.get('_auth_user_id'))
        
        # Logout
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.client.session.get('_auth_user_id'))
        
        # Log in again
        response = self.client.post(reverse('login'), {
            'username': 'integration_test_user',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.client.session.get('_auth_user_id'))
