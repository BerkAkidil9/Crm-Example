"""
Login Integration Test File
This file tests all integration tests related to login.
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
class TestLoginIntegration(TestCase):
    """Login integration tests"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create test user (email verified)
        self.user = User.objects.create_user(
            username='integration_login_user',
            email='integration_login@example.com',
            password='testpass123',
            first_name='Integration',
            last_name='Login',
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
            username='unverified_integration',
            email='unverified_integration@example.com',
            password='testpass123',
            first_name='Unverified',
            last_name='Integration',
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
    
    def test_complete_login_flow_with_username(self):
        """Full login flow test with username"""
        # 1. Go to login page
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')
        
        # 2. Submit login form
        response = self.client.post(reverse('login'), {
            'username': 'integration_login_user',
            'password': 'testpass123'
        })
        
        # 3. Redirect check
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('landing-page'))
        
        # 4. Session check
        self.assertTrue(self.client.session.get('_auth_user_id'))
        
        # 5. Protected page access
        response = self.client.get(reverse('leads:lead-list'))
        self.assertEqual(response.status_code, 200)
    
    def test_complete_login_flow_with_email(self):
        """Full login flow test with email"""
        # 1. Go to login page
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        
        # 2. Submit login form
        response = self.client.post(reverse('login'), {
            'username': 'integration_login@example.com',
            'password': 'testpass123'
        })
        
        # 3. Redirect check
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('landing-page'))
        
        # 4. Session check
        self.assertTrue(self.client.session.get('_auth_user_id'))
        
        # 5. Protected page access
        response = self.client.get(reverse('leads:lead-list'))
        self.assertEqual(response.status_code, 200)
    
    def test_login_flow_with_unverified_email(self):
        """Login flow test with unverified email user"""
        # 1. Go to login page
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        
        # 2. Submit login form
        response = self.client.post(reverse('login'), {
            'username': 'unverified_integration',
            'password': 'testpass123'
        })
        
        # 3. Returns with form errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
        
        # 4. Session should not be created
        self.assertFalse(self.client.session.get('_auth_user_id'))
        
        # 5. Protected page access should be denied
        response = self.client.get(reverse('leads:lead-list'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_login_flow_with_invalid_credentials(self):
        """Login flow test with invalid credentials"""
        # 1. Go to login page
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        
        # 2. Submit login form with wrong password
        response = self.client.post(reverse('login'), {
            'username': 'integration_login_user',
            'password': 'wrongpassword'
        })
        
        # 3. Returns with form errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
        
        # 4. Session should not be created
        self.assertFalse(self.client.session.get('_auth_user_id'))
    
    def test_login_flow_with_nonexistent_user(self):
        """Login flow test with non-existent user"""
        # 1. Go to login page
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        
        # 2. Submit login form with non-existent user
        response = self.client.post(reverse('login'), {
            'username': 'nonexistent_user',
            'password': 'testpass123'
        })
        
        # 3. Returns with form errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
        
        # 4. Session should not be created
        self.assertFalse(self.client.session.get('_auth_user_id'))
    
    def test_login_redirect_authenticated_user(self):
        """Redirect test for logged-in user"""
        # 1. Log in first
        self.client.login(username='integration_login_user', password='testpass123')
        
        # 2. Go to login page
        response = self.client.get(reverse('login'))
        
        # Authenticated user is redirected (redirect_authenticated_user=True)
        self.assertEqual(response.status_code, 302)
    
    def test_login_logout_cycle(self):
        """Login-logout cycle test"""
        # 1. Login
        response = self.client.post(reverse('login'), {
            'username': 'integration_login_user',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.client.session.get('_auth_user_id'))
        
        # 2. Logout
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.client.session.get('_auth_user_id'))
        
        # 3. Tekrar login
        response = self.client.post(reverse('login'), {
            'username': 'integration_login_user',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.client.session.get('_auth_user_id'))
    
    def test_login_with_different_user_types(self):
        """Login test with different user types"""
        # Create agent user
        agent_user = User.objects.create_user(
            username='agent_integration',
            email='agent_integration@example.com',
            password='testpass123',
            first_name='Agent',
            last_name='Integration',
            phone_number='+905552222222',
            date_of_birth='1985-01-01',
            gender='F',
            is_agent=True,
            email_verified=True
        )
        
        # Create UserProfile
        agent_user_profile, created = UserProfile.objects.get_or_create(user=agent_user)
        
        # Login as agent
        response = self.client.post(reverse('login'), {
            'username': 'agent_integration',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.client.session.get('_auth_user_id'))
        
        # Agent page access
        response = self.client.get(reverse('leads:lead-list'))
        self.assertEqual(response.status_code, 200)
    
    def test_login_with_superuser(self):
        """Login test with superuser"""
        # Create superuser
        superuser = User.objects.create_superuser(
            username='superuser_integration',
            email='superuser_integration@example.com',
            password='testpass123',
            first_name='Super',
            last_name='User',
            phone_number='+905553333333',
            date_of_birth='1980-01-01',
            gender='M',
            email_verified=True
        )
        
        # Login as superuser
        response = self.client.post(reverse('login'), {
            'username': 'superuser_integration',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.client.session.get('_auth_user_id'))
        
        # Admin page access
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
    
    def test_login_case_insensitive_credentials(self):
        """Login test with case insensitive credentials"""
        # With username (uppercase)
        response = self.client.post(reverse('login'), {
            'username': 'INTEGRATION_LOGIN_USER',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.client.session.get('_auth_user_id'))
        
        # Logout
        self.client.post(reverse('logout'))
        
        # With email (uppercase)
        response = self.client.post(reverse('login'), {
            'username': 'INTEGRATION_LOGIN@EXAMPLE.COM',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.client.session.get('_auth_user_id'))
    
    def test_login_whitespace_handling(self):
        """Login test with whitespace handling"""
        # With username (leading and trailing whitespace)
        response = self.client.post(reverse('login'), {
            'username': '  integration_login_user  ',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.client.session.get('_auth_user_id'))
        
        # Logout
        self.client.post(reverse('logout'))
        
        # With email (leading and trailing whitespace)
        response = self.client.post(reverse('login'), {
            'username': '  integration_login@example.com  ',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.client.session.get('_auth_user_id'))
    
    def test_login_form_validation_errors(self):
        """Login form validation errors test"""
        # Empty credentials
        response = self.client.post(reverse('login'), {
            'username': '',
            'password': ''
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
        
        # Sadece username
        response = self.client.post(reverse('login'), {
            'username': 'integration_login_user',
            'password': ''
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
        
        # Sadece password
        response = self.client.post(reverse('login'), {
            'username': '',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
    
    def test_login_csrf_protection(self):
        """Login CSRF protection test"""
        # Django test client bypasses CSRF by default
        response = self.client.post(reverse('login'), {
            'username': 'integration_login_user',
            'password': 'testpass123'
        }, follow=False)
        
        # Test client bypasses CSRF - successful login redirects
        self.assertEqual(response.status_code, 302)
    
    def test_login_session_management(self):
        """Login session management test"""
        # Login
        response = self.client.post(reverse('login'), {
            'username': 'integration_login_user',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)
        
        # Check session info
        session = self.client.session
        self.assertTrue(session.get('_auth_user_id'))
        self.assertTrue(session.get('_auth_user_backend'))
        self.assertTrue(session.get('_auth_user_hash'))
        
        # Is user ID correct
        self.assertEqual(int(session.get('_auth_user_id')), self.user.id)
    
    def test_login_redirect_after_login(self):
        """Redirect after login test"""
        # Login with next parameter
        response = self.client.post(reverse('login') + '?next=/leads/', {
            'username': 'integration_login_user',
            'password': 'testpass123'
        })
        
        # Should redirect to leads page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/leads/')
    
    def test_login_with_remember_me(self):
        """Remember me functionality test (if implemented)"""
        # This test can be updated if remember me feature is added
        response = self.client.post(reverse('login'), {
            'username': 'integration_login_user',
            'password': 'testpass123'
        })
        
        # Normal login test
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.client.session.get('_auth_user_id'))
    
    def test_login_performance(self):
        """Login performance test"""
        import time
        
        # Performance test
        start_time = time.time()
        for i in range(10):  # 10 kez test et
            self.client.logout()
            response = self.client.post(reverse('login'), {
                'username': 'integration_login_user',
                'password': 'testpass123'
            })
            self.assertEqual(response.status_code, 302)
        end_time = time.time()
        
        # 10 logins should take less than 5 seconds
        self.assertLess(end_time - start_time, 5.0)
    
    def test_login_with_special_characters(self):
        """Login test with credentials containing special characters"""
        # Create user with special characters
        special_user = User.objects.create_user(
            username='test.user+tag@domain',
            email='special_integration@example.com',
            password='testpass123',
            first_name='Special',
            last_name='Integration',
            phone_number='+905554444444',
            date_of_birth='1990-01-01',
            gender='M',
            is_organisor=True,
            email_verified=True
        )
        
        # Create UserProfile
        special_user_profile, created = UserProfile.objects.get_or_create(user=special_user)
        
        # Create Organisor
        Organisor.objects.create(user=special_user, organisation=special_user_profile)
        
        # Login with username
        response = self.client.post(reverse('login'), {
            'username': 'test.user+tag@domain',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.client.session.get('_auth_user_id'))
        
        # Logout
        self.client.post(reverse('logout'))
        
        # Login with email
        response = self.client.post(reverse('login'), {
            'username': 'special_integration@example.com',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.client.session.get('_auth_user_id'))
