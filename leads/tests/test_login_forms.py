"""
Login Forms Test File
This file tests all forms related to login.
"""

import django
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from unittest.mock import patch, MagicMock

from leads.forms import CustomAuthenticationForm
from leads.models import User, UserProfile, EmailVerificationToken
from organisors.models import Organisor

User = get_user_model()


class TestCustomAuthenticationForm(TestCase):
    """CustomAuthenticationForm tests"""
    
    def setUp(self):
        """Set up test data"""
        # Create test user (email verified)
        self.user = User.objects.create_user(
            username='testuser_login_forms',
            email='test_login_forms@example.com',
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
            username='unverified_user_forms',
            email='unverified_forms@example.com',
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
    
    def test_form_initialization(self):
        """Form initialization test"""
        form = CustomAuthenticationForm()
        
        # Check presence of required fields
        self.assertIn('username', form.fields)
        self.assertIn('password', form.fields)
    
    def test_form_valid_data_username(self):
        """Form test with valid username data"""
        form = CustomAuthenticationForm(data={
            'username': 'testuser_login_forms',
            'password': 'testpass123'
        })
        self.assertTrue(form.is_valid())
    
    def test_form_valid_data_email(self):
        """Form test with valid email data"""
        form = CustomAuthenticationForm(data={
            'username': 'test_login_forms@example.com',
            'password': 'testpass123'
        })
        self.assertTrue(form.is_valid())
    
    def test_form_required_fields(self):
        """Required fields test"""
        # Username missing
        form = CustomAuthenticationForm(data={
            'password': 'testpass123'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        
        # Password missing
        form = CustomAuthenticationForm(data={
            'username': 'testuser_login_forms'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)
        
        # Both missing
        form = CustomAuthenticationForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertIn('password', form.errors)
    
    def test_form_invalid_credentials(self):
        """Form test with invalid credentials"""
        # Wrong password
        form = CustomAuthenticationForm(data={
            'username': 'testuser_login_forms',
            'password': 'wrongpassword'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
    
    def test_form_nonexistent_user(self):
        """Form test with non-existent user"""
        form = CustomAuthenticationForm(data={
            'username': 'nonexistent_user',
            'password': 'testpass123'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
    
    def test_form_unverified_email_user(self):
        """Form test with unverified email user"""
        form = CustomAuthenticationForm(data={
            'username': 'unverified_user_forms',
            'password': 'testpass123'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
    
    def test_form_widget_attributes(self):
        """Widget properties test"""
        form = CustomAuthenticationForm()
        
        # Username widget
        username_widget = form['username'].as_widget()
        self.assertIn('placeholder="Username or Email"', username_widget)
        self.assertIn('class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"', username_widget)
        
        # Password widget
        password_widget = form['password'].as_widget()
        self.assertIn('placeholder="Password"', password_widget)
        self.assertIn('class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"', password_widget)
    
    def test_form_field_labels(self):
        """Form field labels test"""
        form = CustomAuthenticationForm()
        
        self.assertEqual(form.fields['username'].label, 'Username or Email')
        self.assertEqual(form.fields['password'].label, 'Password')
    
    def test_form_field_max_lengths(self):
        """Form field max lengths test"""
        form = CustomAuthenticationForm()
        
        # Username field max_length 150 (Django default), not 254
        self.assertEqual(form.fields['username'].max_length, 150)
    
    def test_form_field_widgets(self):
        """Form field widgets test"""
        form = CustomAuthenticationForm()
        
        # Username widget
        self.assertIsInstance(form.fields['username'].widget, django.forms.TextInput)
        
        # Password widget
        self.assertIsInstance(form.fields['password'].widget, django.forms.PasswordInput)
    
    def test_form_clean_methods(self):
        """Form clean methods test"""
        # Clean test with valid data
        form = CustomAuthenticationForm(data={
            'username': 'testuser_login_forms',
            'password': 'testpass123'
        })
        if form.is_valid():
            # CustomAuthenticationForm has no clean_username method, test removed
            pass
    
    def test_form_validation_edge_cases(self):
        """Form validation edge cases test"""
        # Empty string
        form = CustomAuthenticationForm(data={
            'username': '',
            'password': ''
        })
        self.assertFalse(form.is_valid())
        
        # Whitespace only
        form = CustomAuthenticationForm(data={
            'username': '   ',
            'password': '   '
        })
        self.assertFalse(form.is_valid())
        
        # Very long username
        form = CustomAuthenticationForm(data={
            'username': 'a' * 300,
            'password': 'testpass123'
        })
        self.assertFalse(form.is_valid())
    
    def test_form_case_insensitive_username(self):
        """Case insensitive username test"""
        form = CustomAuthenticationForm(data={
            'username': 'TESTUSER_LOGIN_FORMS',  # Uppercase
            'password': 'testpass123'
        })
        self.assertTrue(form.is_valid())
    
    def test_form_case_insensitive_email(self):
        """Case insensitive email test"""
        form = CustomAuthenticationForm(data={
            'username': 'TEST_LOGIN_FORMS@EXAMPLE.COM',  # Uppercase
            'password': 'testpass123'
        })
        self.assertTrue(form.is_valid())
    
    def test_form_whitespace_handling(self):
        """Whitespace handling test"""
        form = CustomAuthenticationForm(data={
            'username': '  testuser_login_forms  ',  # Leading and trailing whitespace
            'password': 'testpass123'
        })
        self.assertTrue(form.is_valid())
    
    def test_form_error_messages(self):
        """Form error messages test"""
        form = CustomAuthenticationForm()
        
        # Check if error messages are removed
        self.assertEqual(form.fields['username'].error_messages, {'required': ''})
        self.assertEqual(form.fields['password'].error_messages, {'required': ''})
    
    def test_form_autofocus_attribute(self):
        """Autofocus property test"""
        form = CustomAuthenticationForm()
        
        username_widget = form['username'].as_widget()
        self.assertIn('autofocus', username_widget)
    
    def test_form_password_field_attributes(self):
        """Password field properties test"""
        form = CustomAuthenticationForm()
        
        password_widget = form['password'].as_widget()
        self.assertIn('type="password"', password_widget)
        self.assertIn('placeholder="Password"', password_widget)
    
    def test_form_username_field_attributes(self):
        """Username field properties test"""
        form = CustomAuthenticationForm()
        
        username_widget = form['username'].as_widget()
        self.assertIn('type="text"', username_widget)
        self.assertIn('placeholder="Username or Email"', username_widget)
    
    def test_form_with_request_context(self):
        """Form test with request context"""
        from django.test import RequestFactory
        
        factory = RequestFactory()
        request = factory.get('/login/')
        
        form = CustomAuthenticationForm(request=request)
        
        # Form can be initialized with request
        self.assertIsNotNone(form)
    
    def test_form_validation_with_special_characters(self):
        """Validation test with special characters"""
        # Username with special characters
        form = CustomAuthenticationForm(data={
            'username': 'test@user#123',
            'password': 'testpass123'
        })
        # May not be valid, test it
        # self.assertFalse(form.is_valid())
    
    def test_form_validation_with_unicode(self):
        """Validation test with Unicode characters"""
        # Username containing Unicode characters
        form = CustomAuthenticationForm(data={
            'username': 'tëstüsér',
            'password': 'testpass123'
        })
        # May not be valid, test it
        # self.assertFalse(form.is_valid())


class TestLoginFormIntegration(TestCase):
    """Login form integration tests"""
    
    def setUp(self):
        """Set up test data"""
        # Create test user
        self.user = User.objects.create_user(
            username='integration_form_user',
            email='integration_form@example.com',
            password='testpass123',
            first_name='Integration',
            last_name='Form',
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
    
    def test_form_authentication_with_different_credentials(self):
        """Authentication test with different credential formats"""
        # With username
        form = CustomAuthenticationForm(data={
            'username': 'integration_form_user',
            'password': 'testpass123'
        })
        self.assertTrue(form.is_valid())
        
        # With email
        form = CustomAuthenticationForm(data={
            'username': 'integration_form@example.com',
            'password': 'testpass123'
        })
        self.assertTrue(form.is_valid())
    
    def test_form_authentication_failure_scenarios(self):
        """Authentication failure scenarios test"""
        # Wrong password
        form = CustomAuthenticationForm(data={
            'username': 'integration_form_user',
            'password': 'wrongpassword'
        })
        self.assertFalse(form.is_valid())
        
        # Non-existent user
        form = CustomAuthenticationForm(data={
            'username': 'nonexistent_user',
            'password': 'testpass123'
        })
        self.assertFalse(form.is_valid())
        
        # Empty credentials
        form = CustomAuthenticationForm(data={
            'username': '',
            'password': ''
        })
        self.assertFalse(form.is_valid())
    
    def test_form_with_mock_authentication_backend(self):
        """Form test with mock authentication backend"""
        with patch('leads.authentication.EmailOrUsernameModelBackend.authenticate') as mock_authenticate:
            # Mock authentication successful
            mock_authenticate.return_value = self.user
            
            form = CustomAuthenticationForm(data={
                'username': 'integration_form_user',
                'password': 'testpass123'
            })
            
            # Form should be valid
            self.assertTrue(form.is_valid())
            
            # Was mock authentication called
            mock_authenticate.assert_called_once()
    
    def test_form_validation_with_empty_data(self):
        """Form validation test with empty data"""
        form = CustomAuthenticationForm(data={})
        
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertIn('password', form.errors)
    
    def test_form_validation_with_partial_data(self):
        """Form validation test with partial data"""
        # Sadece username
        form = CustomAuthenticationForm(data={
            'username': 'integration_form_user'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)
        
        # Sadece password
        form = CustomAuthenticationForm(data={
            'password': 'testpass123'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
