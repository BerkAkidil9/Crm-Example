"""
Signup Integration Test File
This file contains all signup-related integration tests.
"""

import os
import sys
import django
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core import mail
from django.utils import timezone
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

# Load Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djcrm.settings')
django.setup()

from leads.models import User, UserProfile, EmailVerificationToken
from organisors.models import Organisor

User = get_user_model()


class TestSignupCompleteFlow(TestCase):
    """Complete signup flow integration tests"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        self.valid_signup_data = {
            'username': 'complete_flow_user',
            'email': 'complete_flow@example.com',
            'first_name': 'Complete',
            'last_name': 'Flow',
            'phone_number_0': '+90',
            'phone_number_1': '5551234567',
            'date_of_birth': '1990-01-01',
            'gender': 'M',
            'password1': 'completepass123!',
            'password2': 'completepass123!',
        }
    
    @patch('leads.views.send_mail')
    def test_complete_signup_and_verification_flow(self, mock_send_mail):
        """Complete signup and verification flow test"""
        
        # 1. Go to signup page
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sign Up')
        
        # 2. Submit signup form
        response = self.client.post(reverse('signup'), self.valid_signup_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('verify-email-sent'))
        
        # 3. Check if user was created
        self.assertTrue(User.objects.filter(username='complete_flow_user').exists())
        user = User.objects.get(username='complete_flow_user')
        
        # 4. Are user attributes correct
        self.assertEqual(user.email, 'complete_flow@example.com')
        self.assertEqual(user.first_name, 'Complete')
        self.assertEqual(user.last_name, 'Flow')
        self.assertTrue(user.is_organisor)
        self.assertFalse(user.is_agent)
        self.assertFalse(user.email_verified)
        
        # 5. Was UserProfile created
        self.assertTrue(UserProfile.objects.filter(user=user).exists())
        user_profile = UserProfile.objects.get(user=user)
        
        # 6. Was Organisor created
        self.assertTrue(Organisor.objects.filter(user=user).exists())
        organisor = Organisor.objects.get(user=user)
        self.assertEqual(organisor.organisation, user_profile)
        
        # 7. Was email verification token created
        self.assertTrue(EmailVerificationToken.objects.filter(user=user).exists())
        verification_token = EmailVerificationToken.objects.get(user=user)
        self.assertFalse(verification_token.is_used)
        self.assertFalse(verification_token.is_expired())
        
        # 8. Was email sent
        mock_send_mail.assert_called_once()
        
        # 9. Go to email verification sent page
        response = self.client.get(reverse('verify-email-sent'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'verification')
        
        # 10. Click email verification link
        response = self.client.get(
            reverse('verify-email', kwargs={'token': verification_token.token})
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('verify-email-success'))
        
        # 11. Was user email verified
        updated_user = User.objects.get(pk=user.pk)
        self.assertTrue(updated_user.email_verified)
        
        # 12. Was token marked as used
        updated_token = EmailVerificationToken.objects.get(pk=verification_token.pk)
        self.assertTrue(updated_token.is_used)
        
        # 13. Access login page
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')
    
    def test_signup_flow_with_invalid_data(self):
        """Signup flow with invalid data test"""
        
        # Invalid email format
        invalid_data = self.valid_signup_data.copy()
        invalid_data['email'] = 'invalid-email-format'
        
        response = self.client.post(reverse('signup'), invalid_data)
        self.assertEqual(response.status_code, 200)  # Returns with form errors
        self.assertFalse(User.objects.filter(username='complete_flow_user').exists())
        
        # Password mismatch
        invalid_data = self.valid_signup_data.copy()
        invalid_data['password1'] = 'password123!'
        invalid_data['password2'] = 'differentpassword123!'
        
        response = self.client.post(reverse('signup'), invalid_data)
        self.assertEqual(response.status_code, 200)  # Returns with form errors
        self.assertFalse(User.objects.filter(username='complete_flow_user').exists())
        
        # Eksik zorunlu alanlar
        incomplete_data = {
            'username': 'complete_flow_user',
            'email': 'complete_flow@example.com',
            # Other fields missing
        }
        
        response = self.client.post(reverse('signup'), incomplete_data)
        self.assertEqual(response.status_code, 200)  # Returns with form errors
        self.assertFalse(User.objects.filter(username='complete_flow_user').exists())
    
    def test_signup_flow_with_duplicate_data(self):
        """Signup flow with conflicting data test"""
        
        # Create a user first
        User.objects.create_user(
            username='duplicate_user',
            email='duplicate@example.com',
            password='testpass123',
            phone_number='+905551111111'
        )
        
        # Sign up with same email
        duplicate_data = self.valid_signup_data.copy()
        duplicate_data['email'] = 'duplicate@example.com'
        
        response = self.client.post(reverse('signup'), duplicate_data)
        self.assertEqual(response.status_code, 200)  # Returns with form errors
        self.assertFalse(User.objects.filter(username='complete_flow_user').exists())
        
        # Sign up with same phone number
        duplicate_data = self.valid_signup_data.copy()
        duplicate_data['phone_number_0'] = '+90'
        duplicate_data['phone_number_1'] = '5551111111'
        
        response = self.client.post(reverse('signup'), duplicate_data)
        self.assertEqual(response.status_code, 200)  # Returns with form errors
        self.assertFalse(User.objects.filter(username='complete_flow_user').exists())


class TestEmailVerificationFlow(TestCase):
    """Email verification flow integration tests"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create test user
        self.user = User.objects.create_user(
            username='verification_flow_user',
            email='verification_flow@example.com',
            password='testpass123!',
            first_name='Verification',
            last_name='Flow',
            is_organisor=True,
            email_verified=False
        )
        
        # Create related models
        # UserProfile should be created automatically by signal
        self.user_profile = UserProfile.objects.get(user=self.user)
        self.organisor = Organisor.objects.create(user=self.user, organisation=self.user_profile)
        self.verification_token = EmailVerificationToken.objects.create(user=self.user)
    
    def test_email_verification_success_flow(self):
        """Email verification success flow test"""
        
        # 1. Click email verification link
        response = self.client.get(
            reverse('verify-email', kwargs={'token': self.verification_token.token})
        )
        
        # 2. Should redirect to verification success page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('verify-email-success'))
        
        # 3. Was user email verified
        updated_user = User.objects.get(pk=self.user.pk)
        self.assertTrue(updated_user.email_verified)
        
        # 4. Was token marked as used
        updated_token = EmailVerificationToken.objects.get(pk=self.verification_token.pk)
        self.assertTrue(updated_token.is_used)
    
    def test_email_verification_invalid_token_flow(self):
        """Email verification flow with invalid token test"""
        
        # Invalid token
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
    
    def test_email_verification_expired_token_flow(self):
        """Email verification flow with expired token test"""
        
        # Mark token as expired
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
    
    def test_email_verification_used_token_flow(self):
        """Email verification flow with used token test"""
        
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


class TestSignupModelRelationships(TestCase):
    """Signup model relationships integration tests"""
    
    def setUp(self):
        """Set up test data"""
        self.user_data = {
            'username': 'relationship_test_user',
            'email': 'relationship_test@example.com',
            'password': 'testpass123!',
            'first_name': 'Relationship',
            'last_name': 'Test',
            'phone_number': '+905559876543',  # Correct format for User model
            'date_of_birth': datetime(1985, 5, 15).date(),
            'gender': 'F',
            'is_organisor': True,
            'email_verified': False,
        }
    
    def test_signup_model_creation_and_relationships(self):
        """Signup model creation and relationships test"""
        
        # 1. Create User
        user = User.objects.create_user(**self.user_data)
        
        # 2. UserProfile should be created automatically by signal
        user_profile = UserProfile.objects.get(user=user)
        
        # 3. Create Organisor
        organisor = Organisor.objects.create(user=user, organisation=user_profile)
        
        # 4. Create EmailVerificationToken
        verification_token = EmailVerificationToken.objects.create(user=user)
        
        # Check model counts
        self.assertEqual(User.objects.filter(username='relationship_test_user').count(), 1)
        self.assertEqual(UserProfile.objects.filter(user=user).count(), 1)
        self.assertEqual(Organisor.objects.filter(user=user).count(), 1)
        self.assertEqual(EmailVerificationToken.objects.filter(user=user).count(), 1)
        
        # Check relationships
        self.assertEqual(user.userprofile, user_profile)
        self.assertEqual(user.organisor, organisor)
        self.assertEqual(organisor.user, user)
        self.assertEqual(organisor.organisation, user_profile)
        self.assertEqual(verification_token.user, user)
        
        # Cascade delete test
        user_pk = user.pk
        user_profile_pk = user_profile.pk
        organisor_pk = organisor.pk
        verification_token_pk = verification_token.pk
        
        user.delete()
        
        self.assertFalse(User.objects.filter(pk=user_pk).exists())
        self.assertFalse(UserProfile.objects.filter(pk=user_profile_pk).exists())
        self.assertFalse(Organisor.objects.filter(pk=organisor_pk).exists())
        self.assertFalse(EmailVerificationToken.objects.filter(pk=verification_token_pk).exists())
    
    def test_signup_model_data_consistency(self):
        """Signup model data consistency test"""
        
        # Full signup process
        user = User.objects.create_user(**self.user_data)
        user_profile = UserProfile.objects.get(user=user)
        organisor = Organisor.objects.create(user=user, organisation=user_profile)
        verification_token = EmailVerificationToken.objects.create(user=user)
        
        # Data consistency check
        self.assertEqual(user.is_organisor, True)
        self.assertEqual(user.email_verified, False)
        self.assertEqual(user.userprofile, user_profile)
        self.assertEqual(user.organisor, organisor)
        self.assertEqual(organisor.organisation, user_profile)
        self.assertEqual(verification_token.user, user)
        self.assertFalse(verification_token.is_used)
        self.assertFalse(verification_token.is_expired())
        
        # After email verification
        user.email_verified = True
        user.save()
        verification_token.is_used = True
        verification_token.save()
        
        updated_user = User.objects.get(pk=user.pk)
        updated_token = EmailVerificationToken.objects.get(pk=verification_token.pk)
        
        self.assertTrue(updated_user.email_verified)
        self.assertTrue(updated_token.is_used)


class TestSignupFormIntegration(TestCase):
    """Signup form integration tests"""
    
    def setUp(self):
        """Set up test data"""
        self.valid_data = {
            'username': 'form_integration_user',
            'email': 'form_integration@example.com',
            'first_name': 'Form',
            'last_name': 'Integration',
            'phone_number_0': '+90',
            'phone_number_1': '5551111111',
            'date_of_birth': '1992-03-15',
            'gender': 'M',
            'password1': 'formpass123!',
            'password2': 'formpass123!',
        }
    
    def test_form_save_and_model_creation(self):
        """Form save and model creation integration test"""
        
        from leads.forms import CustomUserCreationForm
        
        # Create and save form
        form = CustomUserCreationForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
        
        user = form.save()
        
        # Was user created in database
        self.assertTrue(User.objects.filter(username='form_integration_user').exists())
        
        saved_user = User.objects.get(username='form_integration_user')
        self.assertEqual(saved_user.email, 'form_integration@example.com')
        self.assertEqual(saved_user.first_name, 'Form')
        self.assertEqual(saved_user.last_name, 'Integration')
        self.assertEqual(saved_user.phone_number, '+905551111111')
        self.assertEqual(saved_user.gender, 'M')
        self.assertEqual(saved_user.date_of_birth.strftime('%Y-%m-%d'), '1992-03-15')
        
        # Was password set correctly
        self.assertTrue(saved_user.check_password('formpass123!'))
    
    def test_form_validation_with_existing_data(self):
        """Form validation integration with existing data test"""
        
        from leads.forms import CustomUserCreationForm
        
        # Create a user first
        User.objects.create_user(
            username='existing_form_user',
            email='existing_form@example.com',
            password='testpass123',
            phone_number='+905552222222'
        )
        
        # Test form with conflicting email
        data = self.valid_data.copy()
        data['email'] = 'existing_form@example.com'
        data['username'] = 'different_username'
        
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        
        # Test form with conflicting phone number
        data = self.valid_data.copy()
        data['phone_number_0'] = '+90'
        data['phone_number_1'] = '5552222222'
        data['username'] = 'different_username2'
        
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('phone_number', form.errors)
        
        # Test form with conflicting username
        data = self.valid_data.copy()
        data['username'] = 'existing_form_user'
        
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)


class TestSignupViewFormIntegration(TestCase):
    """Signup view and form integration tests"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        self.valid_data = {
            'username': 'view_form_integration_user',
            'email': 'view_form_integration@example.com',
            'first_name': 'View',
            'last_name': 'Form',
            'phone_number_0': '+90',
            'phone_number_1': '5553333333',
            'date_of_birth': '1988-07-20',
            'gender': 'F',
            'password1': 'viewformpass123!',
            'password2': 'viewformpass123!',
        }
    
    @patch('leads.views.send_mail')
    def test_signup_view_form_integration(self, mock_send_mail):
        """Signup view and form integration test"""
        
        # 1. Go to signup page
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        
        # Check form class
        from leads.forms import CustomUserCreationForm
        self.assertIsInstance(response.context['form'], CustomUserCreationForm)
        
        # 2. Submit form
        response = self.client.post(reverse('signup'), self.valid_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('verify-email-sent'))
        
        # 3. Was user created
        self.assertTrue(User.objects.filter(username='view_form_integration_user').exists())
        user = User.objects.get(username='view_form_integration_user')
        
        # 4. Are user attributes correct
        self.assertEqual(user.email, 'view_form_integration@example.com')
        self.assertEqual(user.first_name, 'View')
        self.assertEqual(user.last_name, 'Form')
        self.assertTrue(user.is_organisor)
        self.assertFalse(user.is_agent)
        self.assertFalse(user.email_verified)
        
        # 5. Were related models created
        self.assertTrue(UserProfile.objects.filter(user=user).exists())
        self.assertTrue(Organisor.objects.filter(user=user).exists())
        self.assertTrue(EmailVerificationToken.objects.filter(user=user).exists())
        
        # 6. Was email sent
        mock_send_mail.assert_called_once()
    
    def test_signup_view_form_validation_integration(self):
        """Signup view form validation integration test"""
        
        # Submit form with invalid data
        invalid_data = self.valid_data.copy()
        invalid_data['email'] = 'invalid-email-format'
        
        response = self.client.post(reverse('signup'), invalid_data)
        self.assertEqual(response.status_code, 200)  # Returns with form errors
        
        # User was not created
        self.assertFalse(User.objects.filter(username='view_form_integration_user').exists())
        
        # Are form errors in context
        self.assertIn('form', response.context)
        self.assertFalse(response.context['form'].is_valid())


if __name__ == "__main__":
    print("Starting Signup Integration Tests...")
    print("=" * 60)
    
    # Run tests
    import unittest
    unittest.main()
