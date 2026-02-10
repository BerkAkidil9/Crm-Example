"""
Organisors Models Test File
This file tests all models in the organisors module.
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone

from organisors.models import Organisor
from leads.models import User, UserProfile


class TestOrganisorModel(TestCase):
    """Organisor model tests"""
    
    def setUp(self):
        """Set up test data"""
        # Create test user
        self.user = User.objects.create_user(
            username="testuser_organisor_models",
            email="test_organisor_models@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
            phone_number="+905551234567",
            date_of_birth="1990-01-01",
            gender="M",
            is_organisor=True,
            email_verified=True
        )
        
        # Create UserProfile
        self.user_profile, created = UserProfile.objects.get_or_create(user=self.user)
        
        # Create Organisor
        self.organisor = Organisor.objects.create(
            user=self.user,
            organisation=self.user_profile
        )
    
    def test_organisor_creation(self):
        """Organisor creation test"""
        self.assertEqual(self.organisor.user, self.user)
        self.assertEqual(self.organisor.organisation, self.user_profile)
        self.assertIsNotNone(self.organisor)
    
    def test_organisor_str_representation(self):
        """Organisor __str__ method test"""
        self.assertEqual(str(self.organisor), self.user.email)
    
    def test_organisor_verbose_names(self):
        """Organisor verbose name tests"""
        self.assertEqual(Organisor._meta.verbose_name, "Organisor")
        self.assertEqual(Organisor._meta.verbose_name_plural, "Organisors")
    
    def test_organisor_user_relationship(self):
        """Organisor-User relationship test"""
        self.assertEqual(self.organisor.user, self.user)
        self.assertTrue(hasattr(self.user, 'organisor'))
        self.assertEqual(self.user.organisor, self.organisor)
    
    def test_organisor_organisation_relationship(self):
        """Organisor-Organisation relationship test"""
        self.assertEqual(self.organisor.organisation, self.user_profile)
        self.assertIn(self.organisor, self.user_profile.organisor_set.all())
    
    def test_organisor_user_one_to_one(self):
        """Organisor-User OneToOneField test"""
        # Cannot create second organisor for same user
        with self.assertRaises(IntegrityError):
            Organisor.objects.create(
                user=self.user,
                organisation=self.user_profile
            )
    
    def test_organisor_cascade_delete_user(self):
        """When user is deleted Organisor is also deleted test"""
        user_id = self.user.id
        organisor_id = self.organisor.id
        
        # Delete user
        self.user.delete()
        
        # Organisor should also be deleted
        self.assertFalse(Organisor.objects.filter(id=organisor_id).exists())
        self.assertFalse(User.objects.filter(id=user_id).exists())
    
    def test_organisor_cascade_delete_organisation(self):
        """When organisation is deleted Organisor is also deleted test"""
        # Create new organisor
        user2 = User.objects.create_user(
            username="testuser2_organisor_models",
            email="test2_organisor_models@example.com",
            password="testpass123",
            is_organisor=True
        )
        user_profile2, created = UserProfile.objects.get_or_create(user=user2)
        organisor2 = Organisor.objects.create(
            user=user2,
            organisation=user_profile2
        )
        
        organisor_id = organisor2.id
        user_profile_id = user_profile2.id
        
        # Delete UserProfile
        user_profile2.delete()
        
        # Organisor should also be deleted
        self.assertFalse(Organisor.objects.filter(id=organisor_id).exists())
        self.assertFalse(UserProfile.objects.filter(id=user_profile_id).exists())
    
    def test_organisor_multiple_organisations(self):
        """User cannot have multiple organisor records test"""
        # Cannot create organisor with different organisation for same user
        user2 = User.objects.create_user(
            username="testuser3_organisor_models",
            email="test3_organisor_models@example.com",
            password="testpass123",
            is_organisor=True
        )
        user_profile2, created = UserProfile.objects.get_or_create(user=user2)
        
        # Cannot create second organisor with same user
        with self.assertRaises(IntegrityError):
            Organisor.objects.create(
                user=self.user,  # Same user
                organisation=user_profile2  # Different organisation
            )
    
    def test_organisor_model_fields(self):
        """Organisor model fields test"""
        # Check presence of model fields
        self.assertTrue(hasattr(self.organisor, 'user'))
        self.assertTrue(hasattr(self.organisor, 'organisation'))
        self.assertTrue(hasattr(self.organisor, 'id'))
    
    def test_organisor_foreign_key_constraints(self):
        """Organisor foreign key constraints test"""
        # This test checks Django's built-in constraints
        # Foreign key fields are required so None values are not accepted
        # This is checked at database level, not Django ORM level
        
        # Does Organisor model have correct foreign key fields?
        self.assertTrue(hasattr(Organisor._meta.get_field('user'), 'null'))
        self.assertTrue(hasattr(Organisor._meta.get_field('organisation'), 'null'))
        
        # Foreign key fields should be null=False
        self.assertFalse(Organisor._meta.get_field('user').null)
        self.assertFalse(Organisor._meta.get_field('organisation').null)


class TestOrganisorModelRelationships(TestCase):
    """Organisor model relationships tests"""
    
    def setUp(self):
        """Set up test data"""
        # Create admin user
        self.admin_user = User.objects.create_user(
            username="admin_organisor_relationships",
            email="admin_organisor_relationships@example.com",
            password="testpass123",
            first_name="Admin",
            last_name="User",
            phone_number="+905551111111",
            date_of_birth="1985-01-01",
            gender="M",
            is_organisor=True,
            email_verified=True
        )
        
        # Create Admin UserProfile
        self.admin_profile, created = UserProfile.objects.get_or_create(user=self.admin_user)
        
        # Create Admin Organisor
        self.admin_organisor = Organisor.objects.create(
            user=self.admin_user,
            organisation=self.admin_profile
        )
        
        # Create normal user
        self.normal_user = User.objects.create_user(
            username="normal_organisor_relationships",
            email="normal_organisor_relationships@example.com",
            password="testpass123",
            first_name="Normal",
            last_name="User",
            phone_number="+905552222222",
            date_of_birth="1990-01-01",
            gender="F",
            is_organisor=True,
            email_verified=True
        )
        
        # Create normal UserProfile
        self.normal_profile, created = UserProfile.objects.get_or_create(user=self.normal_user)
        
        # Create normal Organisor
        self.normal_organisor = Organisor.objects.create(
            user=self.normal_user,
            organisation=self.admin_profile  # Linked to admin's organisation
        )
    
    def test_organisor_organisation_hierarchy(self):
        """Organisor organisation hierarchy test"""
        # Normal organisor linked to admin's organisation
        self.assertEqual(self.normal_organisor.organisation, self.admin_profile)
        self.assertNotEqual(self.normal_organisor.organisation, self.normal_profile)
    
    def test_organisor_user_profile_consistency(self):
        """Organisor user profile consistency test"""
        # Each organisor has its own user
        self.assertEqual(self.admin_organisor.user, self.admin_user)
        self.assertEqual(self.normal_organisor.user, self.normal_user)
        
        # Users have organisor records
        self.assertEqual(self.admin_user.organisor, self.admin_organisor)
        self.assertEqual(self.normal_user.organisor, self.normal_organisor)
    
    def test_organisor_organisation_access(self):
        """Organisor organisation access test"""
        # Organisors linked to admin's organisation
        admin_organisors = Organisor.objects.filter(organisation=self.admin_profile)
        self.assertIn(self.admin_organisor, admin_organisors)
        self.assertIn(self.normal_organisor, admin_organisors)
        self.assertEqual(admin_organisors.count(), 2)
    
    def test_organisor_user_queries(self):
        """Organisor user queries test"""
        # Access user from organisor
        self.assertEqual(self.admin_organisor.user.username, "admin_organisor_relationships")
        self.assertEqual(self.normal_organisor.user.email, "normal_organisor_relationships@example.com")
        
        # Access organisor from user
        self.assertEqual(self.admin_user.organisor.organisation, self.admin_profile)
        self.assertEqual(self.normal_user.organisor.organisation, self.admin_profile)
    
    def test_organisor_organisation_queries(self):
        """Organisor organisation queries test"""
        # Access organisors from organisation
        organisors = self.admin_profile.organisor_set.all()
        self.assertEqual(organisors.count(), 2)
        self.assertIn(self.admin_organisor, organisors)
        self.assertIn(self.normal_organisor, organisors)
        
        # Access organisation from organisor
        self.assertEqual(self.admin_organisor.organisation.user, self.admin_user)
        self.assertEqual(self.normal_organisor.organisation.user, self.admin_user)


class TestOrganisorModelEdgeCases(TestCase):
    """Organisor model edge cases tests"""
    
    def test_organisor_with_deleted_user(self):
        """Organisor with deleted user test"""
        # Create user
        user = User.objects.create_user(
            username="deleted_user_organisor",
            email="deleted_user_organisor@example.com",
            password="testpass123",
            is_organisor=True
        )
        
        # Create UserProfile
        user_profile, created = UserProfile.objects.get_or_create(user=user)
        
        # Create Organisor
        organisor = Organisor.objects.create(
            user=user,
            organisation=user_profile
        )
        
        # Delete user
        user.delete()
        
        # Organisor should also be deleted
        self.assertFalse(Organisor.objects.filter(id=organisor.id).exists())
    
    def test_organisor_with_deleted_organisation(self):
        """Organisor with deleted organisation test"""
        # Create user
        user = User.objects.create_user(
            username="deleted_org_organisor",
            email="deleted_org_organisor@example.com",
            password="testpass123",
            is_organisor=True
        )
        
        # Create UserProfile
        user_profile, created = UserProfile.objects.get_or_create(user=user)
        
        # Create Organisor
        organisor = Organisor.objects.create(
            user=user,
            organisation=user_profile
        )
        
        # Delete UserProfile
        user_profile.delete()
        
        # Organisor should also be deleted
        self.assertFalse(Organisor.objects.filter(id=organisor.id).exists())
    
    def test_organisor_model_meta_options(self):
        """Organisor model Meta options test"""
        # Check model Meta options
        meta = Organisor._meta
        self.assertEqual(meta.verbose_name, "Organisor")
        self.assertEqual(meta.verbose_name_plural, "Organisors")
        
        # Check model fields
        field_names = [field.name for field in meta.fields]
        self.assertIn('id', field_names)
        self.assertIn('user', field_names)
        self.assertIn('organisation', field_names)
    
    def test_organisor_model_constraints(self):
        """Organisor model constraints test"""
        # OneToOneField constraint
        user = User.objects.create_user(
            username="constraint_test_user",
            email="constraint_test_user@example.com",
            password="testpass123",
            is_organisor=True
        )
        user_profile, created = UserProfile.objects.get_or_create(user=user)
        
        # Create first organisor
        Organisor.objects.create(
            user=user,
            organisation=user_profile
        )
        
        # Cannot create second organisor with same user
        with self.assertRaises(IntegrityError):
            Organisor.objects.create(
                user=user,
                organisation=user_profile
            )
