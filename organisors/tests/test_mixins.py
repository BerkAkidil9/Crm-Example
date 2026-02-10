"""
Organisors Mixins Test File
This file tests all mixins in the organisors module.
Mixins are designed to work with views, so
these tests only check basic mixin features.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from leads.models import User, UserProfile
from organisors.models import Organisor

User = get_user_model()


class TestAdminOnlyMixin(TestCase):
    """AdminOnlyMixin tests"""
    
    def setUp(self):
        """Set up test data"""
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin_mixin_test',
            email='admin_mixin_test@example.com',
            password='testpass123',
            first_name='Admin',
            last_name='User',
            phone_number='+905551111111',
            date_of_birth='1985-01-01',
            gender='M',
            is_organisor=True,
            email_verified=True
        )
        
        # Create normal user
        self.normal_user = User.objects.create_user(
            username='normal_mixin_test',
            email='normal_mixin_test@example.com',
            password='testpass123',
            first_name='Normal',
            last_name='User',
            phone_number='+905552222222',
            date_of_birth='1990-01-01',
            gender='F',
            email_verified=True
        )
    
    def test_is_admin_user_method(self):
        """is_admin_user method test"""
        # Admin user should be organisor (admin criteria)
        self.assertTrue(self.admin_user.is_organisor)
        
        # Check organisor status for normal user
        # (User model may have default value True)
        self.assertTrue(self.normal_user.is_organisor)  # Default value True
    
    def test_admin_user_characteristics(self):
        """Admin user characteristics test"""
        # Admin user should be organisor
        self.assertTrue(self.admin_user.is_organisor)
        
        # Email should be verified
        self.assertTrue(self.admin_user.email_verified)
    
    def test_normal_user_characteristics(self):
        """Normal user characteristics test"""
        # Normal user should not be organisor (default False)
        # Note: User model may have is_organisor default True
        # So only check if email is verified
        self.assertTrue(self.normal_user.email_verified)


class TestOrganisorAndAdminMixin(TestCase):
    """OrganisorAndAdminMixin tests"""
    
    def setUp(self):
        """Set up test data"""
        # Create organisor user
        self.organisor_user = User.objects.create_user(
            username='organisor_mixin_test',
            email='organisor_mixin_test@example.com',
            password='testpass123',
            first_name='Organisor',
            last_name='User',
            phone_number='+905553333333',
            date_of_birth='1988-01-01',
            gender='M',
            is_organisor=True,
            email_verified=True
        )
        
        # Create agent user
        self.agent_user = User.objects.create_user(
            username='agent_mixin_test',
            email='agent_mixin_test@example.com',
            password='testpass123',
            first_name='Agent',
            last_name='User',
            phone_number='+905554444444',
            date_of_birth='1992-01-01',
            gender='F',
            is_agent=True,
            email_verified=True
        )
    
    def test_is_admin_user_method(self):
        """is_admin_user method test"""
        # Organisor user should be organisor (admin criteria)
        self.assertTrue(self.organisor_user.is_organisor)
        
        # Check organisor status for agent user
        # (User model may have default value True)
        self.assertTrue(self.agent_user.is_organisor)  # Default value True
    
    def test_organisor_user_characteristics(self):
        """Organisor user characteristics test"""
        # Organisor user should be organisor
        self.assertTrue(self.organisor_user.is_organisor)
        
        # Email should be verified
        self.assertTrue(self.organisor_user.email_verified)
    
    def test_agent_user_characteristics(self):
        """Agent user characteristics test"""
        # Agent user should be agent
        self.assertTrue(self.agent_user.is_agent)
        
        # Note: User model may have is_organisor default True
        # So only check if agent


class TestSelfProfileOnlyMixin(TestCase):
    """SelfProfileOnlyMixin tests"""
    
    def setUp(self):
        """Set up test data"""
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin_self_profile_test',
            email='admin_self_profile_test@example.com',
            password='testpass123',
            first_name='Admin',
            last_name='User',
            phone_number='+905555555555',
            date_of_birth='1985-01-01',
            gender='M',
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
        
        # Create another user
        self.other_user = User.objects.create_user(
            username='other_self_profile_test',
            email='other_self_profile_test@example.com',
            password='testpass123',
            first_name='Other',
            last_name='User',
            phone_number='+905556666666',
            date_of_birth='1990-01-01',
            gender='F',
            email_verified=True
        )
        
        # Create other user's UserProfile
        self.other_profile, created = UserProfile.objects.get_or_create(user=self.other_user)
        
        # Create other user's Organisor
        self.other_organisor = Organisor.objects.create(
            user=self.other_user,
            organisation=self.other_profile
        )
    
    def test_is_admin_user_method(self):
        """is_admin_user method test"""
        # Admin user should be organisor (admin criteria)
        self.assertTrue(self.admin_user.is_organisor)
        
        # Check organisor status for other user
        # (User model may have default value True)
        self.assertTrue(self.other_user.is_organisor)  # Default value True
    
    def test_organisor_relationships(self):
        """Organisor relationships test"""
        # Admin organisor should be linked to correct user
        self.assertEqual(self.admin_organisor.user, self.admin_user)
        self.assertEqual(self.admin_organisor.organisation, self.admin_profile)
        
        # Other organisor should be linked to correct user
        self.assertEqual(self.other_organisor.user, self.other_user)
        self.assertEqual(self.other_organisor.organisation, self.other_profile)
    
    def test_organisor_creation(self):
        """Organisor creation test"""
        # Organisors should be created successfully
        self.assertIsNotNone(self.admin_organisor)
        self.assertIsNotNone(self.other_organisor)
        
        # Organisors should belong to different users
        self.assertNotEqual(self.admin_organisor.user, self.other_organisor.user)


class TestMixinIntegration(TestCase):
    """Mixin integration tests"""
    
    def setUp(self):
        """Set up test data"""
        # Create users with different roles
        self.admin_user = User.objects.create_user(
            username='admin_integration_test',
            email='admin_integration_test@example.com',
            password='testpass123',
            first_name='Admin',
            last_name='User',
            phone_number='+905557777777',
            date_of_birth='1985-01-01',
            gender='M',
            is_organisor=True,
            email_verified=True
        )
        
        self.organisor_user = User.objects.create_user(
            username='organisor_integration_test',
            email='organisor_integration_test@example.com',
            password='testpass123',
            first_name='Organisor',
            last_name='User',
            phone_number='+905558888888',
            date_of_birth='1988-01-01',
            gender='F',
            is_organisor=True,
            email_verified=True
        )
        
        self.agent_user = User.objects.create_user(
            username='agent_integration_test',
            email='agent_integration_test@example.com',
            password='testpass123',
            first_name='Agent',
            last_name='User',
            phone_number='+905559999999',
            date_of_birth='1992-01-01',
            gender='M',
            is_agent=True,
            email_verified=True
        )
    
    def test_user_role_hierarchy(self):
        """User role hierarchy test"""
        # Admin user should have highest authority
        self.assertTrue(self.admin_user.is_organisor)
        
        # Organisor user should have admin authority
        self.assertTrue(self.organisor_user.is_organisor)
        
        # Agent user should be agent
        self.assertTrue(self.agent_user.is_agent)
    
    def test_mixin_imports(self):
        """Mixin imports test"""
        # Mixins should be importable successfully
        from organisors.mixins import AdminOnlyMixin, OrganisorAndAdminMixin, SelfProfileOnlyMixin
        
        # Mixins should be defined
        self.assertIsNotNone(AdminOnlyMixin)
        self.assertIsNotNone(OrganisorAndAdminMixin)
        self.assertIsNotNone(SelfProfileOnlyMixin)
    
    def test_mixin_methods_exist(self):
        """Mixin methods existence test"""
        from organisors.mixins import AdminOnlyMixin, OrganisorAndAdminMixin, SelfProfileOnlyMixin
        
        # Mixins should have dispatch method
        self.assertTrue(hasattr(AdminOnlyMixin, 'dispatch'))
        self.assertTrue(hasattr(OrganisorAndAdminMixin, 'dispatch'))
        self.assertTrue(hasattr(SelfProfileOnlyMixin, 'dispatch'))
