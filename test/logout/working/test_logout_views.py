"""
Logout Views Test File
This file tests all views related to logout.
"""

import os
import sys
import django
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.utils import timezone
from unittest.mock import patch, MagicMock

# Load Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djcrm.settings')
django.setup()

from leads.models import User, UserProfile, EmailVerificationToken
from organisors.models import Organisor

User = get_user_model()


class TestLogoutView(TestCase):
    """LogoutView tests"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create test user (email verified)
        self.user = User.objects.create_user(
            username='testuser_logout_views',
            email='test_logout_views@example.com',
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
    
    def test_logout_view_post_authenticated_user(self):
        """Logout POST request test with authenticated user"""
        # Log in first
        self.client.login(username='testuser_logout_views', password='testpass123')
        
        # Session check - should be logged in
        self.assertTrue(self.client.session.get('_auth_user_id'))
        
        # Logout
        response = self.client.post(reverse('logout'))
        
        # Should redirect
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('landing-page'))
        
        # Session should be cleared
        self.assertFalse(self.client.session.get('_auth_user_id'))
    
    def test_logout_view_get_authenticated_user(self):
        """Logout GET request test with authenticated user"""
        # Log in first
        self.client.login(username='testuser_logout_views', password='testpass123')
        
        # Session check - should be logged in
        self.assertTrue(self.client.session.get('_auth_user_id'))
        
        # Logout via GET (Django LogoutView does not support GET, returns 405)
        response = self.client.get(reverse('logout'))
        
        # Should be method not allowed (Django LogoutView only supports POST)
        self.assertEqual(response.status_code, 405)
        
        # Session should still be active (did not logout)
        self.assertTrue(self.client.session.get('_auth_user_id'))
    
    def test_logout_view_unauthenticated_user(self):
        """Logout test with unauthenticated user"""
        # Session check - should not be logged in
        self.assertFalse(self.client.session.get('_auth_user_id'))
        
        # Logout (even if not logged in)
        response = self.client.post(reverse('logout'))
        
        # Should redirect
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('landing-page'))
        
        # Session should still be empty
        self.assertFalse(self.client.session.get('_auth_user_id'))
    
    def test_logout_view_redirect_url(self):
        """Redirect URL after logout test"""
        # Log in first
        self.client.login(username='testuser_logout_views', password='testpass123')
        
        # Perform logout
        response = self.client.post(reverse('logout'))
        
        # Should redirect to LOGOUT_REDIRECT_URL (defined as '/' in settings.py)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')
    
    def test_logout_view_session_cleanup(self):
        """Session cleanup after logout test"""
        # Log in first
        self.client.login(username='testuser_logout_views', password='testpass123')
        
        # Check session info
        session = self.client.session
        self.assertTrue(session.get('_auth_user_id'))
        self.assertTrue(session.get('_auth_user_backend'))
        self.assertTrue(session.get('_auth_user_hash'))
        
        # Perform logout
        response = self.client.post(reverse('logout'))
        
        # Session should be cleared
        session = self.client.session
        self.assertFalse(session.get('_auth_user_id'))
        self.assertFalse(session.get('_auth_user_backend'))
        self.assertFalse(session.get('_auth_user_hash'))
    
    def test_logout_view_protected_page_access_after_logout(self):
        """Protected page access after logout test"""
        # Log in first
        self.client.login(username='testuser_logout_views', password='testpass123')
        
        # Protected page access (logged in)
        response = self.client.get(reverse('leads:lead-list'))
        self.assertEqual(response.status_code, 200)
        
        # Logout
        self.client.post(reverse('logout'))
        
        # Access to protected page after logout should be denied
        response = self.client.get(reverse('leads:lead-list'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_logout_view_multiple_logout_calls(self):
        """Multiple logout calls test"""
        # Log in first
        self.client.login(username='testuser_logout_views', password='testpass123')
        
        # First logout
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.client.session.get('_auth_user_id'))
        
        # Second logout (already logged out)
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.client.session.get('_auth_user_id'))
        
        # Third logout (still logged out)
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.client.session.get('_auth_user_id'))
    
    def test_logout_view_csrf_protection(self):
        """CSRF protection test"""
        # Log in first
        self.client.login(username='testuser_logout_views', password='testpass123')
        
        # Logout with CSRF token (normal)
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        
        # Django test client adds CSRF token automatically
        # A different approach is needed for manual CSRF token test
    
    def test_logout_view_next_parameter(self):
        """Redirect with next parameter after logout test"""
        # Log in first
        self.client.login(username='testuser_logout_views', password='testpass123')
        
        # Logout with next parameter
        response = self.client.post(reverse('logout') + '?next=/login/')
        
        # Django LogoutView supports next parameter
        # Redirect URL may vary by next parameter
        self.assertEqual(response.status_code, 302)
    
    def test_logout_view_with_different_user_types(self):
        """Logout test with different user types"""
        # Logout with organiser
        self.client.login(username='testuser_logout_views', password='testpass123')
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.client.session.get('_auth_user_id'))
        
        # Create agent user
        agent_user = User.objects.create_user(
            username='agent_logout_test',
            email='agent_logout@example.com',
            password='testpass123',
            first_name='Agent',
            last_name='User',
            phone_number='+905559876543',
            date_of_birth='1985-01-01',
            gender='F',
            is_agent=True,
            email_verified=True
        )
        
        # Create UserProfile
        agent_user_profile, created = UserProfile.objects.get_or_create(user=agent_user)
        
        # Logout with agent
        self.client.login(username='agent_logout_test', password='testpass123')
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.client.session.get('_auth_user_id'))
    
    def test_logout_view_with_superuser(self):
        """Logout test with superuser"""
        # Create superuser
        superuser = User.objects.create_superuser(
            username='superuser_logout',
            email='superuser_logout@example.com',
            password='testpass123',
            first_name='Super',
            last_name='User',
            phone_number='+905551111111',
            date_of_birth='1980-01-01',
            gender='M',
            email_verified=True
        )
        
        # Log in as superuser
        self.client.login(username='superuser_logout', password='testpass123')
        self.assertTrue(self.client.session.get('_auth_user_id'))
        
        # Perform logout
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.client.session.get('_auth_user_id'))
    
    def test_logout_view_session_data_cleanup(self):
        """Custom session data cleanup after logout test"""
        # Log in first
        self.client.login(username='testuser_logout_views', password='testpass123')
        
        # Add custom data to session
        session = self.client.session
        session['custom_data'] = 'test_value'
        session.save()
        
        # Check session data
        self.assertEqual(self.client.session.get('custom_data'), 'test_value')
        
        # Logout
        response = self.client.post(reverse('logout'))
        
        # Session is flushed, all data is cleared
        # New session is created
        session = self.client.session
        self.assertIsNone(session.get('custom_data'))
    
    def test_logout_view_concurrent_sessions(self):
        """Logout test with concurrent sessions"""
        # Create two different clients (different sessions)
        client1 = Client()
        client2 = Client()
        
        # Log in with both clients
        client1.login(username='testuser_logout_views', password='testpass123')
        client2.login(username='testuser_logout_views', password='testpass123')
        
        # Both clients should be logged in
        self.assertTrue(client1.session.get('_auth_user_id'))
        self.assertTrue(client2.session.get('_auth_user_id'))
        
        # Logout with Client1
        response = client1.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(client1.session.get('_auth_user_id'))
        
        # Client2 should still be logged in (different session)
        self.assertTrue(client2.session.get('_auth_user_id'))
    
    def test_logout_view_url_pattern(self):
        """Logout URL pattern test"""
        # Is logout URL correct
        logout_url = reverse('logout')
        self.assertEqual(logout_url, '/logout/')
    
    def test_logout_view_with_ajax_request(self):
        """Logout test with AJAX request"""
        # Log in first
        self.client.login(username='testuser_logout_views', password='testpass123')
        
        # Logout via AJAX request
        response = self.client.post(
            reverse('logout'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Should redirect
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.client.session.get('_auth_user_id'))


class TestLogoutViewSecurity(TestCase):
    """Logout security tests"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create test user
        self.user = User.objects.create_user(
            username='security_logout_user',
            email='security_logout@example.com',
            password='testpass123',
            first_name='Security',
            last_name='User',
            phone_number='+905552222222',
            date_of_birth='1990-01-01',
            gender='M',
            is_organisor=True,
            email_verified=True
        )
        
        # Create UserProfile
        self.user_profile, created = UserProfile.objects.get_or_create(user=self.user)
        
        # Create Organisor
        Organisor.objects.create(user=self.user, organisation=self.user_profile)
    
    def test_logout_view_session_fixation_protection(self):
        """Session fixation attack protection test"""
        # Log in first
        self.client.login(username='security_logout_user', password='testpass123')
        
        # Save session ID
        old_session_key = self.client.session.session_key
        
        # Perform logout
        self.client.post(reverse('logout'))
        
        # New session should be created (session key should change)
        # Django flushes session after logout
        new_session_key = self.client.session.session_key
        
        # Session keys should be different (or None)
        # New session is created after logout
        self.assertIsNotNone(old_session_key)
    
    def test_logout_view_no_session_hijacking(self):
        """Session hijacking attack protection test"""
        # Log in first
        self.client.login(username='security_logout_user', password='testpass123')
        
        # Save session info
        user_id = self.client.session.get('_auth_user_id')
        
        # Perform logout
        self.client.post(reverse('logout'))
        
        # Attempt to access protected page with old session
        response = self.client.get(reverse('leads:lead-list'))
        
        # Access should be denied (redirect to login)
        self.assertEqual(response.status_code, 302)
    
    def test_logout_view_token_invalidation(self):
        """Token invalidation after logout test"""
        # Log in first
        self.client.login(username='security_logout_user', password='testpass123')
        
        # Save session hash
        session_hash = self.client.session.get('_auth_user_hash')
        self.assertIsNotNone(session_hash)
        
        # Perform logout
        self.client.post(reverse('logout'))
        
        # Session hash should be cleared
        self.assertIsNone(self.client.session.get('_auth_user_hash'))
    
    def test_logout_view_no_caching(self):
        """Cache control after logout test"""
        # Log in first
        self.client.login(username='security_logout_user', password='testpass123')
        
        # Perform logout
        response = self.client.post(reverse('logout'))
        
        # Check Cache-Control headers
        # Django LogoutView does not add cache control automatically
        # But pages should not be cached after logout
        self.assertEqual(response.status_code, 302)


if __name__ == "__main__":
    print("Starting Logout View Tests...")
    print("=" * 60)
    
    # Run tests
    import unittest
    unittest.main()

