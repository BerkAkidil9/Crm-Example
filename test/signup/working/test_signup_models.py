"""
Signup Models Test File
This file tests all signup-related models.
"""

import os
import sys
import django
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta
import uuid

# Load Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djcrm.settings')
django.setup()

from leads.models import User, UserProfile, EmailVerificationToken
from organisors.models import Organisor


class TestUserModel(TestCase):
    """User model tests"""
    
    def setUp(self):
        """Set up test data"""
        self.user_data = {
            'username': 'testuser_model',
            'email': 'test_model@example.com',
            'password': 'testpass123!',
            'first_name': 'Test',
            'last_name': 'User',
            'phone_number': '+905551234567',
            'date_of_birth': datetime(1990, 1, 1).date(),
            'gender': 'M',
        }
    
    def test_user_creation(self):
        """User creation test"""
        user = User.objects.create_user(**self.user_data)
        
        self.assertEqual(user.username, 'testuser_model')
        self.assertEqual(user.email, 'test_model@example.com')
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User')
        self.assertEqual(user.phone_number, '+905551234567')
        self.assertEqual(user.date_of_birth, datetime(1990, 1, 1).date())
        self.assertEqual(user.gender, 'M')
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)
        self.assertTrue(user.is_active)
    
    def test_user_creation_with_organisor_flag(self):
        """User creation with organisor flag test"""
        user_data = self.user_data.copy()
        user_data['is_organisor'] = True
        
        user = User.objects.create_user(**user_data)
        
        self.assertTrue(user.is_organisor)
        self.assertFalse(user.is_agent)
    
    def test_user_creation_with_agent_flag(self):
        """User creation with agent flag test"""
        user_data = self.user_data.copy()
        user_data['username'] = 'testuser_agent_flag'
        user_data['email'] = 'test_agent_flag@example.com'
        user_data['is_agent'] = True
        user_data['is_organisor'] = False  # Explicitly set to False
        
        user = User.objects.create_user(**user_data)
        
        self.assertTrue(user.is_agent)
        self.assertFalse(user.is_organisor)
    
    def test_user_email_verification_default(self):
        """Email verification default value test"""
        user = User.objects.create_user(**self.user_data)
        
        self.assertFalse(user.email_verified)
    
    def test_user_email_verification_set(self):
        """Email verification set test"""
        user = User.objects.create_user(**self.user_data)
        user.email_verified = True
        user.save()
        
        updated_user = User.objects.get(pk=user.pk)
        self.assertTrue(updated_user.email_verified)
    
    def test_user_gender_choices(self):
        """Gender choices test"""
        expected_choices = [
            ('M', 'Male'),
            ('F', 'Female'),
            ('O', 'Other'),
        ]
        
        self.assertEqual(User.GENDER_CHOICES, expected_choices)
    
    def test_user_str_method(self):
        """User __str__ method test"""
        user = User.objects.create_user(**self.user_data)
        
        self.assertEqual(str(user), 'testuser_model')
    
    def test_user_get_full_name(self):
        """User get_full_name method test"""
        user = User.objects.create_user(**self.user_data)
        
        self.assertEqual(user.get_full_name(), 'Test User')
    
    def test_user_get_short_name(self):
        """User get_short_name method test"""
        user = User.objects.create_user(**self.user_data)
        
        self.assertEqual(user.get_short_name(), 'Test')
    
    def test_user_unique_constraints(self):
        """User uniqueness constraints test"""
        # Create first user
        User.objects.create_user(**self.user_data)
        
        # Try to create second user with same email
        with self.assertRaises(Exception):  # IntegrityError or ValidationError
            User.objects.create_user(
                username='different_username',
                email='test_model@example.com',
                password='testpass123!'
            )
        
        # Try to create second user with same phone number
        with self.assertRaises(Exception):  # IntegrityError or ValidationError
            User.objects.create_user(
                username='different_username2',
                email='different@example.com',
                password='testpass123!',
                phone_number='+905551234567'
            )


class TestUserProfileModel(TestCase):
    """UserProfile model tests"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser_profile',
            email='test_profile@example.com',
            password='testpass123!'
        )
    
    def test_userprofile_creation(self):
        """UserProfile creation test"""
        # Create a new user for test
        test_user = User.objects.create_user(
            username='testuser_profile_creation',
            email='test_profile_creation@example.com',
            password='testpass123!'
        )
        # UserProfile should already be created by signal
        profile = UserProfile.objects.get(user=test_user)
        
        self.assertEqual(profile.user, test_user)
        self.assertEqual(str(profile), 'testuser_profile_creation')
    
    def test_userprofile_get_or_create(self):
        """UserProfile get_or_create test"""
        # Create new user for test
        test_user = User.objects.create_user(
            username='testuser_profile_get_or_create',
            email='test_profile_get_or_create@example.com',
            password='testpass123!'
        )
        
        # UserProfile should already be created by signal
        profile, created = UserProfile.objects.get_or_create(user=test_user)
        
        self.assertFalse(created)  # Already created by signal
        self.assertEqual(profile.user, test_user)
        
        # Second call - should not create
        profile2, created2 = UserProfile.objects.get_or_create(user=test_user)
        
        self.assertFalse(created2)
        self.assertEqual(profile, profile2)
    
    def test_userprofile_unique_constraint(self):
        """UserProfile uniqueness constraint test"""
        # Create a new user for test
        test_user = User.objects.create_user(
            username='testuser_profile_unique',
            email='test_profile_unique@example.com',
            password='testpass123!'
        )
        
        # UserProfile should already be created by signal
        self.assertTrue(UserProfile.objects.filter(user=test_user).exists())
        
        # Try to create second profile for same user
        with self.assertRaises(Exception):  # IntegrityError
            UserProfile.objects.create(user=test_user)
    
    def test_userprofile_str_method(self):
        """UserProfile __str__ method test"""
        # Create new user for test
        test_user = User.objects.create_user(
            username='testuser_profile_str',
            email='test_profile_str@example.com',
            password='testpass123!'
        )
        # UserProfile should already be created by signal
        profile = UserProfile.objects.get(user=test_user)
        
        self.assertEqual(str(profile), 'testuser_profile_str')


class TestEmailVerificationTokenModel(TestCase):
    """EmailVerificationToken model tests"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser_token',
            email='test_token@example.com',
            password='testpass123!'
        )
    
    def test_email_verification_token_creation(self):
        """EmailVerificationToken creation test"""
        token = EmailVerificationToken.objects.create(user=self.user)
        
        self.assertEqual(token.user, self.user)
        self.assertIsInstance(token.token, uuid.UUID)
        self.assertFalse(token.is_used)
        self.assertIsNotNone(token.created_at)
    
    def test_email_verification_token_str_method(self):
        """EmailVerificationToken __str__ method test"""
        token = EmailVerificationToken.objects.create(user=self.user)
        
        expected_str = f"Verification token for {self.user.email}"
        self.assertEqual(str(token), expected_str)
    
    def test_email_verification_token_is_expired_false(self):
        """EmailVerificationToken not expired test"""
        token = EmailVerificationToken.objects.create(user=self.user)
        
        # Token newly created, should not be expired
        self.assertFalse(token.is_expired())
    
    def test_email_verification_token_is_expired_true(self):
        """EmailVerificationToken expired test"""
        token = EmailVerificationToken.objects.create(user=self.user)
        
        # Make token as if created 25 hours ago (24-hour window expired)
        expired_time = timezone.now() - timedelta(hours=25)
        token.created_at = expired_time
        token.save()
        
        self.assertTrue(token.is_expired())
    
    def test_email_verification_token_is_expired_boundary(self):
        """EmailVerificationToken time limit test"""
        token = EmailVerificationToken.objects.create(user=self.user)
        
        # Make token as if created 24 hours + 1 minute ago
        boundary_time = timezone.now() - timedelta(hours=24, minutes=1)
        token.created_at = boundary_time
        token.save()
        
        # Should be considered expired after 24 hours
        self.assertTrue(token.is_expired())
    
    def test_email_verification_token_multiple_tokens_per_user(self):
        """Multiple tokens per user test"""
        # Create multiple tokens for same user
        token1 = EmailVerificationToken.objects.create(user=self.user)
        token2 = EmailVerificationToken.objects.create(user=self.user)
        
        # Both tokens should be created
        self.assertEqual(EmailVerificationToken.objects.filter(user=self.user).count(), 2)
        
        # Tokens should be different
        self.assertNotEqual(token1.token, token2.token)
    
    def test_email_verification_token_mark_as_used(self):
        """EmailVerificationToken mark as used test"""
        token = EmailVerificationToken.objects.create(user=self.user)
        
        self.assertFalse(token.is_used)
        
        # Mark token as used
        token.is_used = True
        token.save()
        
        updated_token = EmailVerificationToken.objects.get(pk=token.pk)
        self.assertTrue(updated_token.is_used)
    
    def test_email_verification_token_cascade_delete(self):
        """EmailVerificationToken cascade delete test"""
        token = EmailVerificationToken.objects.create(user=self.user)
        
        # Delete user
        self.user.delete()
        
        # Token should also be deleted
        self.assertFalse(EmailVerificationToken.objects.filter(pk=token.pk).exists())


class TestOrganisorModel(TestCase):
    """Organisor model tests"""
    
    def setUp(self):
        """Set up test data"""
        # In this test class do not create user in setUp
        # Each test will create its own user
        pass
    
    def test_organisor_creation(self):
        """Organisor creation test"""
        # Create new user for test
        test_user = User.objects.create_user(
            username='testuser_organisor_creation',
            email='test_organisor_creation@example.com',
            password='testpass123!',
            is_organisor=True
        )
        # UserProfile should already be created by signal
        test_user_profile = UserProfile.objects.get(user=test_user)
        
        organisor = Organisor.objects.create(
            user=test_user,
            organisation=test_user_profile
        )
        
        self.assertEqual(organisor.user, test_user)
        self.assertEqual(organisor.organisation, test_user_profile)
        self.assertEqual(str(organisor), 'test_organisor_creation@example.com')
    
    def test_organisor_str_method(self):
        """Organisor __str__ method test"""
        # Create new user for test
        test_user = User.objects.create_user(
            username='testuser_organisor_str',
            email='test_organisor_str@example.com',
            password='testpass123!',
            is_organisor=True
        )
        # UserProfile should already be created by signal
        test_user_profile = UserProfile.objects.get(user=test_user)
        
        organisor = Organisor.objects.create(
            user=test_user,
            organisation=test_user_profile
        )
        
        self.assertEqual(str(organisor), 'test_organisor_str@example.com')
    
    def test_organisor_cascade_delete(self):
        """Organisor cascade delete test"""
        # Create new user for test
        test_user = User.objects.create_user(
            username='testuser_organisor_cascade',
            email='test_organisor_cascade@example.com',
            password='testpass123!',
            is_organisor=True
        )
        # UserProfile should already be created by signal
        test_user_profile = UserProfile.objects.get(user=test_user)
        
        organisor = Organisor.objects.create(
            user=test_user,
            organisation=test_user_profile
        )
        
        # Delete user
        test_user.delete()
        
        # Organisor should also be deleted
        self.assertFalse(Organisor.objects.filter(pk=organisor.pk).exists())


class TestSignupModelIntegration(TestCase):
    """Signup model integration tests"""
    
    def setUp(self):
        """Set up test data"""
        self.user_data = {
            'username': 'integration_test_user',
            'email': 'integration_test@example.com',
            'password': 'testpass123!',
            'first_name': 'Integration',
            'last_name': 'Test',
            'phone_number': '+905559876543',
            'date_of_birth': datetime(1985, 5, 15).date(),
            'gender': 'F',
            'is_organisor': True,
            'email_verified': False,
        }
    
    def test_complete_signup_model_creation(self):
        """Complete signup model creation test"""
        # Create unique user data for test
        user_data = self.user_data.copy()
        user_data['username'] = 'integration_test_user_complete'
        user_data['email'] = 'integration_test_complete@example.com'
        
        # 1. Create user
        user = User.objects.create_user(**user_data)
        
        # 2. UserProfile should already be created by signal
        user_profile = UserProfile.objects.get(user=user)
        
        # 3. Create organisor
        organisor = Organisor.objects.create(
            user=user,
            organisation=user_profile
        )
        
        # 4. Create EmailVerificationToken
        verification_token = EmailVerificationToken.objects.create(user=user)
        
        # All models created correctly?
        self.assertEqual(User.objects.filter(username='integration_test_user_complete').count(), 1)
        self.assertEqual(UserProfile.objects.filter(user=user).count(), 1)
        self.assertEqual(Organisor.objects.filter(user=user).count(), 1)
        self.assertEqual(EmailVerificationToken.objects.filter(user=user).count(), 1)
        
        # Relationships correct?
        self.assertEqual(organisor.user, user)
        self.assertEqual(organisor.organisation, user_profile)
        self.assertEqual(verification_token.user, user)
    
    def test_signup_model_relationships(self):
        """Signup model relationships test"""
        # Create unique user data for test
        user_data = self.user_data.copy()
        user_data['username'] = 'integration_test_user_relationships'
        user_data['email'] = 'integration_test_relationships@example.com'
        
        # Full signup flow
        user = User.objects.create_user(**user_data)
        user_profile = UserProfile.objects.get(user=user)
        organisor = Organisor.objects.create(user=user, organisation=user_profile)
        verification_token = EmailVerificationToken.objects.create(user=user)
        
        # Access other models from User
        self.assertEqual(user.userprofile, user_profile)
        self.assertEqual(user.organisor, organisor)
        self.assertTrue(EmailVerificationToken.objects.filter(user=user).exists())
        
        # Access User from UserProfile
        self.assertEqual(user_profile.user, user)
        
        # Access User and UserProfile from Organisor
        self.assertEqual(organisor.user, user)
        self.assertEqual(organisor.organisation, user_profile)
        
        # Access User from EmailVerificationToken
        self.assertEqual(verification_token.user, user)
    
    def test_signup_model_cascade_operations(self):
        """Signup model cascade operations test"""
        # Create unique user data for test
        user_data = self.user_data.copy()
        user_data['username'] = 'integration_test_user_cascade'
        user_data['email'] = 'integration_test_cascade@example.com'
        
        # Full signup flow
        user = User.objects.create_user(**user_data)
        user_profile = UserProfile.objects.get(user=user)
        organisor = Organisor.objects.create(user=user, organisation=user_profile)
        verification_token = EmailVerificationToken.objects.create(user=user)
        
        user_pk = user.pk
        user_profile_pk = user_profile.pk
        organisor_pk = organisor.pk
        verification_token_pk = verification_token.pk
        
        # Delete user
        user.delete()
        
        # All related models should be deleted
        self.assertFalse(User.objects.filter(pk=user_pk).exists())
        self.assertFalse(UserProfile.objects.filter(pk=user_profile_pk).exists())
        self.assertFalse(Organisor.objects.filter(pk=organisor_pk).exists())
        self.assertFalse(EmailVerificationToken.objects.filter(pk=verification_token_pk).exists())
    
    def test_signup_model_data_integrity(self):
        """Signup model data integrity test"""
        # Create unique user data for test
        user_data = self.user_data.copy()
        user_data['username'] = 'integration_test_user_data_consistency'
        user_data['email'] = 'integration_test_data_consistency@example.com'
        
        # Full signup flow
        user = User.objects.create_user(**user_data)
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
    
    def test_signup_model_validation(self):
        """Signup model validation test"""
        # Model validation tests
        
        # Empty username - Django does not accept this
        with self.assertRaises(ValueError):
            User.objects.create_user(
                username='',
                email='test@example.com',
                password='testpass123!'
            )
        
        # Test that model validation works
        user = User.objects.create_user(
            username='validation_test_user',
            email='validation@example.com',
            password='testpass123!'
        )
        
        # User created successfully
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'validation_test_user')
        
        # Empty username
        with self.assertRaises(Exception):
            User.objects.create_user(
                username='',
                email='test@example.com',
                password='testpass123!'
            )


if __name__ == "__main__":
    print("Starting Signup Model Tests...")
    print("=" * 60)
    
    # Run tests
    import unittest
    unittest.main()
