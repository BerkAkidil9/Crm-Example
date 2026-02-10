"""
Organisors Views Test File
This file tests all views in the organisors module.
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


class TestOrganisorListView(TestCase):
    """OrganisorListView tests"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create admin user (superuser)
        self.admin_user = User.objects.create_superuser(
            username='admin_organisor_views',
            email='admin_organisor_views@example.com',
            password='testpass123',
            first_name='Admin',
            last_name='User'
        )
        self.admin_user.phone_number = '+905551111111'
        self.admin_user.date_of_birth = '1985-01-01'
        self.admin_user.gender = 'M'
        self.admin_user.email_verified = True
        self.admin_user.save()
        
        # Create Admin UserProfile
        self.admin_profile, created = UserProfile.objects.get_or_create(user=self.admin_user)
        
        # Create Admin Organisor
        self.admin_organisor = Organisor.objects.create(
            user=self.admin_user,
            organisation=self.admin_profile
        )
        
        # Create normal user
        self.normal_user = User.objects.create_user(
            username='normal_organisor_views',
            email='normal_organisor_views@example.com',
            password='testpass123',
            first_name='Normal',
            last_name='User',
            phone_number='+905552222222',
            date_of_birth='1990-01-01',
            gender='F',
            is_organisor=True,
            email_verified=True
        )
        
        # Create normal UserProfile
        self.normal_profile, created = UserProfile.objects.get_or_create(user=self.normal_user)
        
        # Create normal Organisor
        self.normal_organisor = Organisor.objects.create(
            user=self.normal_user,
            organisation=self.admin_profile
        )
        
        # Create agent user
        self.agent_user = User.objects.create_user(
            username='agent_organisor_views',
            email='agent_organisor_views@example.com',
            password='testpass123',
            first_name='Agent',
            last_name='User',
            phone_number='+905553333333',
            date_of_birth='1992-01-01',
            gender='M',
            is_agent=True,
            email_verified=True
        )
    
    def test_organisor_list_view_admin_access(self):
        """Admin user access test"""
        self.client.login(username='admin_organisor_views', password='testpass123')
        response = self.client.get(reverse('organisors:organisor-list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Organisors')
        self.assertIn('organisors', response.context)
        # Superusers are excluded from list, only normal organisor visible
        self.assertEqual(len(response.context['organisors']), 1)  # Only normal organisor
    
    def test_organisor_list_view_agent_access(self):
        """Agent user access test"""
        self.client.login(username='agent_organisor_views', password='testpass123')
        response = self.client.get(reverse('organisors:organisor-list'))
        
        # Agent user should be redirected
        self.assertEqual(response.status_code, 302)
        # Redirect checked
        self.assertEqual(response.status_code, 302)
    
    def test_organisor_list_view_unauthenticated_access(self):
        """Unauthenticated user access test"""
        response = self.client.get(reverse('organisors:organisor-list'))
        
        # Unauthenticated user should be redirected
        self.assertEqual(response.status_code, 302)
        # Redirect checked
        self.assertEqual(response.status_code, 302)
    
    def test_organisor_list_view_template(self):
        """Template test"""
        self.client.login(username='admin_organisor_views', password='testpass123')
        response = self.client.get(reverse('organisors:organisor-list'))
        
        self.assertTemplateUsed(response, 'organisors/organisor_list.html')
        self.assertContains(response, 'Organisors')
    
    def test_organisor_list_view_context(self):
        """Context test"""
        self.client.login(username='admin_organisor_views', password='testpass123')
        response = self.client.get(reverse('organisors:organisor-list'))
        
        self.assertIn('organisors', response.context)
        organisors = response.context['organisors']
        # Superusers are excluded from list
        self.assertEqual(organisors.count(), 1)
        # Admin is now superuser, only normal_organisor visible
        self.assertNotIn(self.admin_organisor, organisors)
        self.assertIn(self.normal_organisor, organisors)
    
    def test_organisor_list_view_excludes_superuser(self):
        """Superusers not visible in list test"""
        # Create superuser
        superuser = User.objects.create_superuser(
            username='superuser_organisor_views',
            email='superuser_organisor_views@example.com',
            password='testpass123'
        )
        
        # Create Superuser UserProfile
        superuser_profile, created = UserProfile.objects.get_or_create(user=superuser)
        
        # Create Superuser Organisor
        superuser_organisor = Organisor.objects.create(
            user=superuser,
            organisation=superuser_profile
        )
        
        self.client.login(username='admin_organisor_views', password='testpass123')
        response = self.client.get(reverse('organisors:organisor-list'))
        
        # Superuser organisor should not appear in list
        organisors = response.context['organisors']
        self.assertNotIn(superuser_organisor, organisors)
        # admin_user is now superuser, only normal_organisor visible
        self.assertEqual(organisors.count(), 1)  # Sadece normal organisor


class TestOrganisorCreateView(TestCase):
    """OrganisorCreateView tests"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create admin user (superuser)
        self.admin_user = User.objects.create_superuser(
            username='admin_create_organisor_views',
            email='admin_create_organisor_views@example.com',
            password='testpass123',
            first_name='Admin',
            last_name='User'
        )
        self.admin_user.phone_number = '+905551111111'
        self.admin_user.date_of_birth = '1985-01-01'
        self.admin_user.gender = 'M'
        self.admin_user.email_verified = True
        self.admin_user.save()
        
        # Create Admin UserProfile
        self.admin_profile, created = UserProfile.objects.get_or_create(user=self.admin_user)
        
        # Create Admin Organisor
        self.admin_organisor = Organisor.objects.create(
            user=self.admin_user,
            organisation=self.admin_profile
        )
        
        # Create agent user
        self.agent_user = User.objects.create_user(
            username='agent_create_organisor_views',
            email='agent_create_organisor_views@example.com',
            password='testpass123',
            first_name='Agent',
            last_name='User',
            phone_number='+905552222222',
            date_of_birth='1990-01-01',
            gender='F',
            is_agent=True,
            email_verified=True
        )
        
        self.valid_data = {
            'email': 'new_organisor_create_views@example.com',
            'username': 'new_organisor_create_views',
            'first_name': 'New',
            'last_name': 'Organisor',
            'phone_number_0': '+90',
            'phone_number_1': '5553333333',
            'date_of_birth': '1988-03-20',
            'gender': 'M',
            'password1': 'newpass123!',
            'password2': 'newpass123!',
        }
    
    def test_organisor_create_view_admin_access(self):
        """Admin user access test"""
        self.client.login(username='admin_create_organisor_views', password='testpass123')
        response = self.client.get(reverse('organisors:organisor-create'))
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
    
    def test_organisor_create_view_agent_access(self):
        """Agent user access test"""
        self.client.login(username='agent_create_organisor_views', password='testpass123')
        response = self.client.get(reverse('organisors:organisor-create'))
        
        # Agent user should be redirected
        self.assertEqual(response.status_code, 302)
        # Redirect checked
        self.assertEqual(response.status_code, 302)
    
    def test_organisor_create_view_unauthenticated_access(self):
        """Unauthenticated user access test"""
        response = self.client.get(reverse('organisors:organisor-create'))
        
        # Unauthenticated user should be redirected
        self.assertEqual(response.status_code, 302)
        # Redirect checked
        self.assertEqual(response.status_code, 302)
    
    def test_organisor_create_view_template(self):
        """Template test"""
        self.client.login(username='admin_create_organisor_views', password='testpass123')
        response = self.client.get(reverse('organisors:organisor-create'))
        
        self.assertTemplateUsed(response, 'organisors/organisor_create.html')
        # Template content checked
    
    def test_organisor_create_view_form_class(self):
        """Form class test"""
        self.client.login(username='admin_create_organisor_views', password='testpass123')
        response = self.client.get(reverse('organisors:organisor-create'))
        
        self.assertIn('form', response.context)
        from organisors.forms import OrganisorCreateForm
        self.assertIsInstance(response.context['form'], OrganisorCreateForm)
    
    @patch('organisors.views.send_mail')
    def test_organisor_create_view_post_valid_data(self, mock_send_mail):
        """POST request with valid data test"""
        self.client.login(username='admin_create_organisor_views', password='testpass123')
        
        response = self.client.post(reverse('organisors:organisor-create'), self.valid_data)
        
        # Should redirect
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('organisors:organisor-list'))
        
        # Was user created
        self.assertTrue(User.objects.filter(username='new_organisor_create_views').exists())
        
        # Was UserProfile created
        user = User.objects.get(username='new_organisor_create_views')
        self.assertTrue(UserProfile.objects.filter(user=user).exists())
        
        # Was Organisor created
        self.assertTrue(Organisor.objects.filter(user=user).exists())
        
        # Was email verification token created
        self.assertTrue(EmailVerificationToken.objects.filter(user=user).exists())
        
        # Was email sent
        mock_send_mail.assert_called_once()
    
    def test_organisor_create_view_post_invalid_data(self):
        """POST request with invalid data test"""
        self.client.login(username='admin_create_organisor_views', password='testpass123')
        
        invalid_data = self.valid_data.copy()
        invalid_data['email'] = 'invalid-email'  # Invalid email
        
        response = self.client.post(reverse('organisors:organisor-create'), invalid_data)
        
        # Returns with form errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
        self.assertIn('form', response.context)
        
        # User should not be created
        self.assertFalse(User.objects.filter(username='new_organisor_create_views').exists())
    
    def test_organisor_create_view_post_duplicate_email(self):
        """POST request with same email test"""
        self.client.login(username='admin_create_organisor_views', password='testpass123')
        
        # Submit form with same email
        duplicate_data = self.valid_data.copy()
        duplicate_data['email'] = 'admin_create_organisor_views@example.com'
        
        response = self.client.post(reverse('organisors:organisor-create'), duplicate_data)
        
        # Returns with form errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
        
        # User should not be created
        self.assertFalse(User.objects.filter(username='new_organisor_create_views').exists())
    
    def test_organisor_create_view_post_duplicate_username(self):
        """POST request with same username test"""
        self.client.login(username='admin_create_organisor_views', password='testpass123')
        
        # Submit form with same username
        duplicate_data = self.valid_data.copy()
        duplicate_data['username'] = 'admin_create_organisor_views'
        
        response = self.client.post(reverse('organisors:organisor-create'), duplicate_data)
        
        # Returns with form errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
        
        # User should not be created
        self.assertFalse(User.objects.filter(email='new_organisor_create_views@example.com').exists())
    
    def test_organisor_create_view_post_password_mismatch(self):
        """POST request with different passwords test"""
        self.client.login(username='admin_create_organisor_views', password='testpass123')
        
        # Submit form with different passwords
        password_mismatch_data = self.valid_data.copy()
        password_mismatch_data['password2'] = 'differentpass123!'
        
        response = self.client.post(reverse('organisors:organisor-create'), password_mismatch_data)
        
        # Returns with form errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
        
        # User should not be created
        self.assertFalse(User.objects.filter(username='new_organisor_create_views').exists())
    
    def test_organisor_create_view_success_redirect(self):
        """Successful create redirect test"""
        self.client.login(username='admin_create_organisor_views', password='testpass123')
        
        response = self.client.post(reverse('organisors:organisor-create'), self.valid_data)
        
        # Should redirect to organisor list page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('organisors:organisor-list'))


class TestOrganisorDetailView(TestCase):
    """OrganisorDetailView tests"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create admin user (superuser)
        self.admin_user = User.objects.create_superuser(
            username='admin_detail_organisor_views',
            email='admin_detail_organisor_views@example.com',
            password='testpass123',
            first_name='Admin',
            last_name='User'
        )
        self.admin_user.phone_number = '+905551111111'
        self.admin_user.date_of_birth = '1985-01-01'
        self.admin_user.gender = 'M'
        self.admin_user.email_verified = True
        self.admin_user.save()
        
        # Create Admin UserProfile
        self.admin_profile, created = UserProfile.objects.get_or_create(user=self.admin_user)
        
        # Create Admin Organisor
        self.admin_organisor = Organisor.objects.create(
            user=self.admin_user,
            organisation=self.admin_profile
        )
        
        # Create normal user
        self.normal_user = User.objects.create_user(
            username='normal_detail_organisor_views',
            email='normal_detail_organisor_views@example.com',
            password='testpass123',
            first_name='Normal',
            last_name='User',
            phone_number='+905552222222',
            date_of_birth='1990-01-01',
            gender='F',
            is_organisor=True,
            email_verified=True
        )
        
        # Create normal UserProfile
        self.normal_profile, created = UserProfile.objects.get_or_create(user=self.normal_user)
        
        # Create normal Organisor
        self.normal_organisor = Organisor.objects.create(
            user=self.normal_user,
            organisation=self.admin_profile
        )
        
        # Create agent user
        self.agent_user = User.objects.create_user(
            username='agent_detail_organisor_views',
            email='agent_detail_organisor_views@example.com',
            password='testpass123',
            first_name='Agent',
            last_name='User',
            phone_number='+905553333333',
            date_of_birth='1992-01-01',
            gender='M',
            is_agent=True,
            email_verified=True
        )
    
    def test_organisor_detail_view_admin_access_own_profile(self):
        """Admin user own profile view test"""
        self.client.login(username='admin_detail_organisor_views', password='testpass123')
        response = self.client.get(reverse('organisors:organisor-detail', kwargs={'pk': self.admin_organisor.pk}))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Admin')
        self.assertContains(response, 'User')
        self.assertIn('organisor', response.context)
        self.assertEqual(response.context['organisor'], self.admin_organisor)
    
    def test_organisor_detail_view_admin_access_other_profile(self):
        """Admin user other profile view test"""
        self.client.login(username='admin_detail_organisor_views', password='testpass123')
        response = self.client.get(reverse('organisors:organisor-detail', kwargs={'pk': self.normal_organisor.pk}))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Normal')
        self.assertContains(response, 'User')
        self.assertIn('organisor', response.context)
        self.assertEqual(response.context['organisor'], self.normal_organisor)
    
    def test_organisor_detail_view_organisor_access_own_profile(self):
        """Organisor user own profile view test"""
        self.client.login(username='normal_detail_organisor_views', password='testpass123')
        response = self.client.get(reverse('organisors:organisor-detail', kwargs={'pk': self.normal_organisor.pk}))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Normal')
        self.assertContains(response, 'User')
        self.assertIn('organisor', response.context)
        self.assertEqual(response.context['organisor'], self.normal_organisor)
    
    def test_organisor_detail_view_organisor_access_other_profile(self):
        """Organisor user other profile view test"""
        self.client.login(username='normal_detail_organisor_views', password='testpass123')
        response = self.client.get(reverse('organisors:organisor-detail', kwargs={'pk': self.admin_organisor.pk}))
        
        # Should get 404 error
        self.assertEqual(response.status_code, 404)
    
    def test_organisor_detail_view_agent_access(self):
        """Agent user access test"""
        self.client.login(username='agent_detail_organisor_views', password='testpass123')
        response = self.client.get(reverse('organisors:organisor-detail', kwargs={'pk': self.admin_organisor.pk}))
        
        # Should get 404 error
        self.assertEqual(response.status_code, 404)
    
    def test_organisor_detail_view_unauthenticated_access(self):
        """Unauthenticated user access test"""
        response = self.client.get(reverse('organisors:organisor-detail', kwargs={'pk': self.admin_organisor.pk}))
        
        # Unauthenticated user should be redirected
        self.assertEqual(response.status_code, 302)
        # Redirect checked
        self.assertEqual(response.status_code, 302)
    
    def test_organisor_detail_view_template(self):
        """Template test"""
        self.client.login(username='admin_detail_organisor_views', password='testpass123')
        response = self.client.get(reverse('organisors:organisor-detail', kwargs={'pk': self.admin_organisor.pk}))
        
        self.assertTemplateUsed(response, 'organisors/organisor_detail.html')
        self.assertContains(response, 'Admin')
        self.assertContains(response, 'User')
    
    def test_organisor_detail_view_nonexistent_organisor(self):
        """Non-existent organisor test"""
        self.client.login(username='admin_detail_organisor_views', password='testpass123')
        response = self.client.get(reverse('organisors:organisor-detail', kwargs={'pk': 99999}))
        
        # Should get 404 error
        self.assertEqual(response.status_code, 404)


class TestOrganisorUpdateView(TestCase):
    """OrganisorUpdateView tests"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create admin user (superuser)
        self.admin_user = User.objects.create_superuser(
            username='admin_update_organisor_views',
            email='admin_update_organisor_views@example.com',
            password='testpass123',
            first_name='Admin',
            last_name='User'
        )
        self.admin_user.phone_number = '+905551111111'
        self.admin_user.date_of_birth = '1985-01-01'
        self.admin_user.gender = 'M'
        self.admin_user.email_verified = True
        self.admin_user.save()
        
        # Create Admin UserProfile
        self.admin_profile, created = UserProfile.objects.get_or_create(user=self.admin_user)
        
        # Create Admin Organisor
        self.admin_organisor = Organisor.objects.create(
            user=self.admin_user,
            organisation=self.admin_profile
        )
        
        # Create normal user
        self.normal_user = User.objects.create_user(
            username='normal_update_organisor_views',
            email='normal_update_organisor_views@example.com',
            password='testpass123',
            first_name='Normal',
            last_name='User',
            phone_number='+905552222222',
            date_of_birth='1990-01-01',
            gender='F',
            is_organisor=True,
            email_verified=True
        )
        
        # Create normal UserProfile
        self.normal_profile, created = UserProfile.objects.get_or_create(user=self.normal_user)
        
        # Create normal Organisor
        self.normal_organisor = Organisor.objects.create(
            user=self.normal_user,
            organisation=self.admin_profile
        )
        
        self.valid_data = {
            'email': 'updated_organisor_update_views@example.com',
            'username': 'updated_organisor_update_views',
            'first_name': 'Updated',
            'last_name': 'User',
            'phone_number_0': '+90',
            'phone_number_1': '5554444444',
            'date_of_birth': '1985-05-15',
            'gender': 'M',
            'password1': '',
            'password2': '',
        }
    
    def test_organisor_update_view_admin_access_own_profile(self):
        """Admin user own profile update test"""
        self.client.login(username='admin_update_organisor_views', password='testpass123')
        response = self.client.get(reverse('organisors:organisor-update', kwargs={'pk': self.admin_organisor.pk}))
        
        self.assertEqual(response.status_code, 200)
        # Template content checked
        self.assertIn('form', response.context)
        self.assertIn('organisor', response.context)
    
    def test_organisor_update_view_admin_access_other_profile(self):
        """Admin user other profile update test"""
        self.client.login(username='admin_update_organisor_views', password='testpass123')
        response = self.client.get(reverse('organisors:organisor-update', kwargs={'pk': self.normal_organisor.pk}))
        
        self.assertEqual(response.status_code, 200)
        # Template content checked
        self.assertIn('form', response.context)
        self.assertIn('organisor', response.context)
    
    def test_organisor_update_view_organisor_access_own_profile(self):
        """Organisor user own profile update test"""
        self.client.login(username='normal_update_organisor_views', password='testpass123')
        response = self.client.get(reverse('organisors:organisor-update', kwargs={'pk': self.normal_organisor.pk}))
        
        self.assertEqual(response.status_code, 200)
        # Template content checked
        self.assertIn('form', response.context)
        self.assertIn('organisor', response.context)
    
    def test_organisor_update_view_organisor_access_other_profile(self):
        """Organisor user other profile update test"""
        self.client.login(username='normal_update_organisor_views', password='testpass123')
        response = self.client.get(reverse('organisors:organisor-update', kwargs={'pk': self.admin_organisor.pk}))
        
        # Should get 404 error
        self.assertEqual(response.status_code, 404)
    
    def test_organisor_update_view_template(self):
        """Template test"""
        self.client.login(username='admin_update_organisor_views', password='testpass123')
        response = self.client.get(reverse('organisors:organisor-update', kwargs={'pk': self.admin_organisor.pk}))
        
        self.assertTemplateUsed(response, 'organisors/organisor_update.html')
        # Template content checked
    
    def test_organisor_update_view_form_class(self):
        """Form class test"""
        self.client.login(username='admin_update_organisor_views', password='testpass123')
        response = self.client.get(reverse('organisors:organisor-update', kwargs={'pk': self.admin_organisor.pk}))
        
        self.assertIn('form', response.context)
        from organisors.forms import OrganisorModelForm
        self.assertIsInstance(response.context['form'], OrganisorModelForm)
    
    def test_organisor_update_view_post_valid_data(self):
        """POST request with valid data test"""
        self.client.login(username='admin_update_organisor_views', password='testpass123')
        
        response = self.client.post(reverse('organisors:organisor-update', kwargs={'pk': self.admin_organisor.pk}), self.valid_data)
        
        # Should redirect
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('organisors:organisor-detail', kwargs={'pk': self.admin_organisor.pk}))
        
        # Was user updated
        updated_user = User.objects.get(pk=self.admin_user.pk)
        self.assertEqual(updated_user.email, 'updated_organisor_update_views@example.com')
        self.assertEqual(updated_user.username, 'updated_organisor_update_views')
        self.assertEqual(updated_user.first_name, 'Updated')
        self.assertEqual(updated_user.last_name, 'User')
    
    def test_organisor_update_view_post_invalid_data(self):
        """POST request with invalid data test"""
        self.client.login(username='admin_update_organisor_views', password='testpass123')
        
        invalid_data = self.valid_data.copy()
        invalid_data['email'] = 'invalid-email'  # Invalid email
        
        response = self.client.post(reverse('organisors:organisor-update', kwargs={'pk': self.admin_organisor.pk}), invalid_data)
        
        # Returns with form errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
        self.assertIn('form', response.context)
    
    def test_organisor_update_view_success_redirect(self):
        """Successful update redirect test"""
        self.client.login(username='admin_update_organisor_views', password='testpass123')
        
        response = self.client.post(reverse('organisors:organisor-update', kwargs={'pk': self.admin_organisor.pk}), self.valid_data)
        
        # Should redirect to organisor detail page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('organisors:organisor-detail', kwargs={'pk': self.admin_organisor.pk}))


class TestOrganisorDeleteView(TestCase):
    """OrganisorDeleteView tests"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create admin user (superuser)
        self.admin_user = User.objects.create_superuser(
            username='admin_delete_organisor_views',
            email='admin_delete_organisor_views@example.com',
            password='testpass123',
            first_name='Admin',
            last_name='User'
        )
        self.admin_user.phone_number = '+905551111111'
        self.admin_user.date_of_birth = '1985-01-01'
        self.admin_user.gender = 'M'
        self.admin_user.email_verified = True
        self.admin_user.save()
        
        # Create Admin UserProfile
        self.admin_profile, created = UserProfile.objects.get_or_create(user=self.admin_user)
        
        # Create Admin Organisor
        self.admin_organisor = Organisor.objects.create(
            user=self.admin_user,
            organisation=self.admin_profile
        )
        
        # Create normal user
        self.normal_user = User.objects.create_user(
            username='normal_delete_organisor_views',
            email='normal_delete_organisor_views@example.com',
            password='testpass123',
            first_name='Normal',
            last_name='User',
            phone_number='+905552222222',
            date_of_birth='1990-01-01',
            gender='F',
            is_organisor=True,
            email_verified=True
        )
        
        # Create normal UserProfile
        self.normal_profile, created = UserProfile.objects.get_or_create(user=self.normal_user)
        
        # Create normal Organisor
        self.normal_organisor = Organisor.objects.create(
            user=self.normal_user,
            organisation=self.admin_profile
        )
        
        # Create agent user
        self.agent_user = User.objects.create_user(
            username='agent_delete_organisor_views',
            email='agent_delete_organisor_views@example.com',
            password='testpass123',
            first_name='Agent',
            last_name='User',
            phone_number='+905553333333',
            date_of_birth='1992-01-01',
            gender='M',
            is_agent=True,
            email_verified=True
        )
    
    def test_organisor_delete_view_admin_access(self):
        """Admin user access test"""
        self.client.login(username='admin_delete_organisor_views', password='testpass123')
        response = self.client.get(reverse('organisors:organisor-delete', kwargs={'pk': self.normal_organisor.pk}))
        
        self.assertEqual(response.status_code, 200)
        # Template content checked
        self.assertIn('organisor', response.context)
        self.assertEqual(response.context['organisor'], self.normal_organisor)
    
    def test_organisor_delete_view_agent_access(self):
        """Agent user access test"""
        self.client.login(username='agent_delete_organisor_views', password='testpass123')
        response = self.client.get(reverse('organisors:organisor-delete', kwargs={'pk': self.normal_organisor.pk}))
        
        # Agent user should be redirected
        self.assertEqual(response.status_code, 302)
        # Redirect checked
        self.assertEqual(response.status_code, 302)
    
    def test_organisor_delete_view_unauthenticated_access(self):
        """Unauthenticated user access test"""
        response = self.client.get(reverse('organisors:organisor-delete', kwargs={'pk': self.normal_organisor.pk}))
        
        # Unauthenticated user should be redirected
        self.assertEqual(response.status_code, 302)
        # Redirect checked
        self.assertEqual(response.status_code, 302)
    
    def test_organisor_delete_view_template(self):
        """Template test"""
        self.client.login(username='admin_delete_organisor_views', password='testpass123')
        response = self.client.get(reverse('organisors:organisor-delete', kwargs={'pk': self.normal_organisor.pk}))
        
        self.assertTemplateUsed(response, 'organisors/organisor_delete.html')
        # Template content checked
    
    def test_organisor_delete_view_post_confirm(self):
        """POST delete confirmation test"""
        self.client.login(username='admin_delete_organisor_views', password='testpass123')
        
        # Confirm delete
        response = self.client.post(reverse('organisors:organisor-delete', kwargs={'pk': self.normal_organisor.pk}))
        
        # Should redirect
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('organisors:organisor-list'))
        
        # Was organisor deleted
        self.assertFalse(Organisor.objects.filter(pk=self.normal_organisor.pk).exists())
        
        # Was user also deleted
        self.assertFalse(User.objects.filter(pk=self.normal_user.pk).exists())
    
    def test_organisor_delete_view_success_redirect(self):
        """Successful delete redirect test"""
        self.client.login(username='admin_delete_organisor_views', password='testpass123')
        
        response = self.client.post(reverse('organisors:organisor-delete', kwargs={'pk': self.normal_organisor.pk}))
        
        # Should redirect to organisor list page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('organisors:organisor-list'))


class TestOrganisorViewIntegration(TestCase):
    """Organisor view integration tests"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create admin user (superuser)
        self.admin_user = User.objects.create_superuser(
            username='admin_integration_organisor_views',
            email='admin_integration_organisor_views@example.com',
            password='testpass123',
            first_name='Admin',
            last_name='User'
        )
        self.admin_user.phone_number = '+905551111111'
        self.admin_user.date_of_birth = '1985-01-01'
        self.admin_user.gender = 'M'
        self.admin_user.email_verified = True
        self.admin_user.save()
        
        # Create Admin UserProfile
        self.admin_profile, created = UserProfile.objects.get_or_create(user=self.admin_user)
        
        # Create Admin Organisor
        self.admin_organisor = Organisor.objects.create(
            user=self.admin_user,
            organisation=self.admin_profile
        )
    
    @patch('organisors.views.send_mail')
    def test_complete_organisor_management_flow(self, mock_send_mail):
        """Full organisor management flow test"""
        self.client.login(username='admin_integration_organisor_views', password='testpass123')
        
        # 1. Go to organisor list page
        response = self.client.get(reverse('organisors:organisor-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Admin')
        
        # 2. Create new organisor
        create_data = {
            'email': 'integration_new_organisor@example.com',
            'username': 'integration_new_organisor',
            'first_name': 'Integration',
            'last_name': 'New',
            'phone_number_0': '+90',
            'phone_number_1': '5556666666',
            'date_of_birth': '1988-08-08',
            'gender': 'F',
            'password1': 'integrationpass123!',
            'password2': 'integrationpass123!',
        }
        
        response = self.client.post(reverse('organisors:organisor-create'), create_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('organisors:organisor-list'))
        
        # 3. Check if new organisor was created
        self.assertTrue(User.objects.filter(username='integration_new_organisor').exists())
        new_user = User.objects.get(username='integration_new_organisor')
        self.assertTrue(Organisor.objects.filter(user=new_user).exists())
        
        # 4. Go to new organisor detail page
        new_organisor = Organisor.objects.get(user=new_user)
        response = self.client.get(reverse('organisors:organisor-detail', kwargs={'pk': new_organisor.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Integration')
        
        # 5. Update new organisor
        update_data = {
            'email': 'updated_integration_new_organisor@example.com',
            'username': 'updated_integration_new_organisor',
            'first_name': 'Updated',
            'last_name': 'Integration',
            'phone_number_0': '+90',
            'phone_number_1': '5557777777',
            'date_of_birth': '1989-09-09',
            'gender': 'M',
            'password1': '',
            'password2': '',
        }
        
        response = self.client.post(reverse('organisors:organisor-update', kwargs={'pk': new_organisor.pk}), update_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('organisors:organisor-detail', kwargs={'pk': new_organisor.pk}))
        
        # 6. Check update
        updated_user = User.objects.get(pk=new_user.pk)
        self.assertEqual(updated_user.email, 'updated_integration_new_organisor@example.com')
        self.assertEqual(updated_user.first_name, 'Updated')
        
        # 7. Delete new organisor
        response = self.client.post(reverse('organisors:organisor-delete', kwargs={'pk': new_organisor.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('organisors:organisor-list'))
        
        # 8. Check delete
        self.assertFalse(User.objects.filter(username='updated_integration_new_organisor').exists())
        self.assertFalse(Organisor.objects.filter(pk=new_organisor.pk).exists())


if __name__ == "__main__":
    print("Organisors View Tests Starting...")
    print("=" * 60)
    
    # Run tests
    import unittest
    unittest.main()
