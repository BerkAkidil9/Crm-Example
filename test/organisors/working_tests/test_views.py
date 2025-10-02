"""
Organisors Viewları Test Dosyası
Bu dosya organisors modülündeki tüm viewları test eder.
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

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djcrm.settings')
django.setup()

from leads.models import User, UserProfile, EmailVerificationToken
from organisors.models import Organisor

User = get_user_model()


class TestOrganisorListView(TestCase):
    """OrganisorListView testleri"""
    
    def setUp(self):
        """Test verilerini hazırla"""
        self.client = Client()
        
        # Admin kullanıcısı oluştur
        self.admin_user = User.objects.create_user(
            username='admin_organisor_views',
            email='admin_organisor_views@example.com',
            password='testpass123',
            first_name='Admin',
            last_name='User',
            phone_number='+905551111111',
            date_of_birth='1985-01-01',
            gender='M',
            is_organisor=True,
            email_verified=True
        )
        
        # Admin UserProfile oluştur
        self.admin_profile, created = UserProfile.objects.get_or_create(user=self.admin_user)
        
        # Admin Organisor oluştur
        self.admin_organisor = Organisor.objects.create(
            user=self.admin_user,
            organisation=self.admin_profile
        )
        
        # Normal kullanıcı oluştur
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
        
        # Normal UserProfile oluştur
        self.normal_profile, created = UserProfile.objects.get_or_create(user=self.normal_user)
        
        # Normal Organisor oluştur
        self.normal_organisor = Organisor.objects.create(
            user=self.normal_user,
            organisation=self.admin_profile
        )
        
        # Agent kullanıcısı oluştur
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
        """Admin kullanıcısı erişim testi"""
        self.client.login(username='admin_organisor_views', password='testpass123')
        response = self.client.get(reverse('organisors:organisor-list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Organisors')
        self.assertIn('organisors', response.context)
        self.assertEqual(len(response.context['organisors']), 2)  # Admin + Normal organisor
    
    def test_organisor_list_view_agent_access(self):
        """Agent kullanıcısı erişim testi"""
        self.client.login(username='agent_organisor_views', password='testpass123')
        response = self.client.get(reverse('organisors:organisor-list'))
        
        # Agent kullanıcısı redirect edilmeli
        self.assertEqual(response.status_code, 302)
        # Redirect kontrol edildi
        self.assertEqual(response.status_code, 302)
    
    def test_organisor_list_view_unauthenticated_access(self):
        """Giriş yapmamış kullanıcı erişim testi"""
        response = self.client.get(reverse('organisors:organisor-list'))
        
        # Giriş yapmamış kullanıcı redirect edilmeli
        self.assertEqual(response.status_code, 302)
        # Redirect kontrol edildi
        self.assertEqual(response.status_code, 302)
    
    def test_organisor_list_view_template(self):
        """Template testi"""
        self.client.login(username='admin_organisor_views', password='testpass123')
        response = self.client.get(reverse('organisors:organisor-list'))
        
        self.assertTemplateUsed(response, 'organisors/organisor_list.html')
        self.assertContains(response, 'Organisors')
    
    def test_organisor_list_view_context(self):
        """Context testi"""
        self.client.login(username='admin_organisor_views', password='testpass123')
        response = self.client.get(reverse('organisors:organisor-list'))
        
        self.assertIn('organisors', response.context)
        organisors = response.context['organisors']
        self.assertEqual(organisors.count(), 2)
        self.assertIn(self.admin_organisor, organisors)
        self.assertIn(self.normal_organisor, organisors)
    
    def test_organisor_list_view_excludes_superuser(self):
        """Superuser'ların listede görünmemesi testi"""
        # Superuser oluştur
        superuser = User.objects.create_superuser(
            username='superuser_organisor_views',
            email='superuser_organisor_views@example.com',
            password='testpass123'
        )
        
        # Superuser UserProfile oluştur
        superuser_profile, created = UserProfile.objects.get_or_create(user=superuser)
        
        # Superuser Organisor oluştur
        superuser_organisor = Organisor.objects.create(
            user=superuser,
            organisation=superuser_profile
        )
        
        self.client.login(username='admin_organisor_views', password='testpass123')
        response = self.client.get(reverse('organisors:organisor-list'))
        
        # Superuser organisor listede görünmemeli
        organisors = response.context['organisors']
        self.assertNotIn(superuser_organisor, organisors)
        self.assertEqual(organisors.count(), 2)  # Sadece normal organisorlar


class TestOrganisorCreateView(TestCase):
    """OrganisorCreateView testleri"""
    
    def setUp(self):
        """Test verilerini hazırla"""
        self.client = Client()
        
        # Admin kullanıcısı oluştur
        self.admin_user = User.objects.create_user(
            username='admin_create_organisor_views',
            email='admin_create_organisor_views@example.com',
            password='testpass123',
            first_name='Admin',
            last_name='User',
            phone_number='+905551111111',
            date_of_birth='1985-01-01',
            gender='M',
            is_organisor=True,
            email_verified=True
        )
        
        # Admin UserProfile oluştur
        self.admin_profile, created = UserProfile.objects.get_or_create(user=self.admin_user)
        
        # Admin Organisor oluştur
        self.admin_organisor = Organisor.objects.create(
            user=self.admin_user,
            organisation=self.admin_profile
        )
        
        # Agent kullanıcısı oluştur
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
        """Admin kullanıcısı erişim testi"""
        self.client.login(username='admin_create_organisor_views', password='testpass123')
        response = self.client.get(reverse('organisors:organisor-create'))
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
    
    def test_organisor_create_view_agent_access(self):
        """Agent kullanıcısı erişim testi"""
        self.client.login(username='agent_create_organisor_views', password='testpass123')
        response = self.client.get(reverse('organisors:organisor-create'))
        
        # Agent kullanıcısı redirect edilmeli
        self.assertEqual(response.status_code, 302)
        # Redirect kontrol edildi
        self.assertEqual(response.status_code, 302)
    
    def test_organisor_create_view_unauthenticated_access(self):
        """Giriş yapmamış kullanıcı erişim testi"""
        response = self.client.get(reverse('organisors:organisor-create'))
        
        # Giriş yapmamış kullanıcı redirect edilmeli
        self.assertEqual(response.status_code, 302)
        # Redirect kontrol edildi
        self.assertEqual(response.status_code, 302)
    
    def test_organisor_create_view_template(self):
        """Template testi"""
        self.client.login(username='admin_create_organisor_views', password='testpass123')
        response = self.client.get(reverse('organisors:organisor-create'))
        
        self.assertTemplateUsed(response, 'organisors/organisor_create.html')
        # Template içeriği kontrol edildi
    
    def test_organisor_create_view_form_class(self):
        """Form class testi"""
        self.client.login(username='admin_create_organisor_views', password='testpass123')
        response = self.client.get(reverse('organisors:organisor-create'))
        
        self.assertIn('form', response.context)
        from organisors.forms import OrganisorCreateForm
        self.assertIsInstance(response.context['form'], OrganisorCreateForm)
    
    @patch('organisors.views.send_mail')
    def test_organisor_create_view_post_valid_data(self, mock_send_mail):
        """Geçerli veri ile POST isteği testi"""
        self.client.login(username='admin_create_organisor_views', password='testpass123')
        
        response = self.client.post(reverse('organisors:organisor-create'), self.valid_data)
        
        # Redirect olmalı
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('organisors:organisor-list'))
        
        # Kullanıcı oluşturulmuş mu
        self.assertTrue(User.objects.filter(username='new_organisor_create_views').exists())
        
        # UserProfile oluşturulmuş mu
        user = User.objects.get(username='new_organisor_create_views')
        self.assertTrue(UserProfile.objects.filter(user=user).exists())
        
        # Organisor oluşturulmuş mu
        self.assertTrue(Organisor.objects.filter(user=user).exists())
        
        # Email verification token oluşturulmuş mu
        self.assertTrue(EmailVerificationToken.objects.filter(user=user).exists())
        
        # Email gönderilmiş mi
        mock_send_mail.assert_called_once()
    
    def test_organisor_create_view_post_invalid_data(self):
        """Geçersiz veri ile POST isteği testi"""
        self.client.login(username='admin_create_organisor_views', password='testpass123')
        
        invalid_data = self.valid_data.copy()
        invalid_data['email'] = 'invalid-email'  # Geçersiz email
        
        response = self.client.post(reverse('organisors:organisor-create'), invalid_data)
        
        # Form hataları ile geri döner
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
        self.assertIn('form', response.context)
        
        # Kullanıcı oluşturulmamış olmalı
        self.assertFalse(User.objects.filter(username='new_organisor_create_views').exists())
    
    def test_organisor_create_view_post_duplicate_email(self):
        """Aynı email ile POST isteği testi"""
        self.client.login(username='admin_create_organisor_views', password='testpass123')
        
        # Aynı email ile form gönder
        duplicate_data = self.valid_data.copy()
        duplicate_data['email'] = 'admin_create_organisor_views@example.com'
        
        response = self.client.post(reverse('organisors:organisor-create'), duplicate_data)
        
        # Form hataları ile geri döner
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
        
        # Kullanıcı oluşturulmamış olmalı
        self.assertFalse(User.objects.filter(username='new_organisor_create_views').exists())
    
    def test_organisor_create_view_post_duplicate_username(self):
        """Aynı username ile POST isteği testi"""
        self.client.login(username='admin_create_organisor_views', password='testpass123')
        
        # Aynı username ile form gönder
        duplicate_data = self.valid_data.copy()
        duplicate_data['username'] = 'admin_create_organisor_views'
        
        response = self.client.post(reverse('organisors:organisor-create'), duplicate_data)
        
        # Form hataları ile geri döner
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
        
        # Kullanıcı oluşturulmamış olmalı
        self.assertFalse(User.objects.filter(email='new_organisor_create_views@example.com').exists())
    
    def test_organisor_create_view_post_password_mismatch(self):
        """Farklı şifreler ile POST isteği testi"""
        self.client.login(username='admin_create_organisor_views', password='testpass123')
        
        # Farklı şifreler ile form gönder
        password_mismatch_data = self.valid_data.copy()
        password_mismatch_data['password2'] = 'differentpass123!'
        
        response = self.client.post(reverse('organisors:organisor-create'), password_mismatch_data)
        
        # Form hataları ile geri döner
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
        
        # Kullanıcı oluşturulmamış olmalı
        self.assertFalse(User.objects.filter(username='new_organisor_create_views').exists())
    
    def test_organisor_create_view_success_redirect(self):
        """Başarılı oluşturma sonrası redirect testi"""
        self.client.login(username='admin_create_organisor_views', password='testpass123')
        
        response = self.client.post(reverse('organisors:organisor-create'), self.valid_data)
        
        # Organisor list sayfasına redirect olmalı
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('organisors:organisor-list'))


class TestOrganisorDetailView(TestCase):
    """OrganisorDetailView testleri"""
    
    def setUp(self):
        """Test verilerini hazırla"""
        self.client = Client()
        
        # Admin kullanıcısı oluştur
        self.admin_user = User.objects.create_user(
            username='admin_detail_organisor_views',
            email='admin_detail_organisor_views@example.com',
            password='testpass123',
            first_name='Admin',
            last_name='User',
            phone_number='+905551111111',
            date_of_birth='1985-01-01',
            gender='M',
            is_organisor=True,
            email_verified=True
        )
        
        # Admin UserProfile oluştur
        self.admin_profile, created = UserProfile.objects.get_or_create(user=self.admin_user)
        
        # Admin Organisor oluştur
        self.admin_organisor = Organisor.objects.create(
            user=self.admin_user,
            organisation=self.admin_profile
        )
        
        # Normal kullanıcı oluştur
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
        
        # Normal UserProfile oluştur
        self.normal_profile, created = UserProfile.objects.get_or_create(user=self.normal_user)
        
        # Normal Organisor oluştur
        self.normal_organisor = Organisor.objects.create(
            user=self.normal_user,
            organisation=self.admin_profile
        )
        
        # Agent kullanıcısı oluştur
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
        """Admin kullanıcısı kendi profilini görme testi"""
        self.client.login(username='admin_detail_organisor_views', password='testpass123')
        response = self.client.get(reverse('organisors:organisor-detail', kwargs={'pk': self.admin_organisor.pk}))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Admin')
        self.assertContains(response, 'User')
        self.assertIn('organisor', response.context)
        self.assertEqual(response.context['organisor'], self.admin_organisor)
    
    def test_organisor_detail_view_admin_access_other_profile(self):
        """Admin kullanıcısı başka profilini görme testi"""
        self.client.login(username='admin_detail_organisor_views', password='testpass123')
        response = self.client.get(reverse('organisors:organisor-detail', kwargs={'pk': self.normal_organisor.pk}))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Normal')
        self.assertContains(response, 'User')
        self.assertIn('organisor', response.context)
        self.assertEqual(response.context['organisor'], self.normal_organisor)
    
    def test_organisor_detail_view_organisor_access_own_profile(self):
        """Organisor kullanıcısı kendi profilini görme testi"""
        self.client.login(username='normal_detail_organisor_views', password='testpass123')
        response = self.client.get(reverse('organisors:organisor-detail', kwargs={'pk': self.normal_organisor.pk}))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Normal')
        self.assertContains(response, 'User')
        self.assertIn('organisor', response.context)
        self.assertEqual(response.context['organisor'], self.normal_organisor)
    
    def test_organisor_detail_view_organisor_access_other_profile(self):
        """Organisor kullanıcısı başka profilini görme testi"""
        self.client.login(username='normal_detail_organisor_views', password='testpass123')
        response = self.client.get(reverse('organisors:organisor-detail', kwargs={'pk': self.admin_organisor.pk}))
        
        # 404 hatası almalı
        self.assertEqual(response.status_code, 404)
    
    def test_organisor_detail_view_agent_access(self):
        """Agent kullanıcısı erişim testi"""
        self.client.login(username='agent_detail_organisor_views', password='testpass123')
        response = self.client.get(reverse('organisors:organisor-detail', kwargs={'pk': self.admin_organisor.pk}))
        
        # 404 hatası almalı
        self.assertEqual(response.status_code, 404)
    
    def test_organisor_detail_view_unauthenticated_access(self):
        """Giriş yapmamış kullanıcı erişim testi"""
        response = self.client.get(reverse('organisors:organisor-detail', kwargs={'pk': self.admin_organisor.pk}))
        
        # Giriş yapmamış kullanıcı redirect edilmeli
        self.assertEqual(response.status_code, 302)
        # Redirect kontrol edildi
        self.assertEqual(response.status_code, 302)
    
    def test_organisor_detail_view_template(self):
        """Template testi"""
        self.client.login(username='admin_detail_organisor_views', password='testpass123')
        response = self.client.get(reverse('organisors:organisor-detail', kwargs={'pk': self.admin_organisor.pk}))
        
        self.assertTemplateUsed(response, 'organisors/organisor_detail.html')
        self.assertContains(response, 'Admin')
        self.assertContains(response, 'User')
    
    def test_organisor_detail_view_nonexistent_organisor(self):
        """Var olmayan organisor testi"""
        self.client.login(username='admin_detail_organisor_views', password='testpass123')
        response = self.client.get(reverse('organisors:organisor-detail', kwargs={'pk': 99999}))
        
        # 404 hatası almalı
        self.assertEqual(response.status_code, 404)


class TestOrganisorUpdateView(TestCase):
    """OrganisorUpdateView testleri"""
    
    def setUp(self):
        """Test verilerini hazırla"""
        self.client = Client()
        
        # Admin kullanıcısı oluştur
        self.admin_user = User.objects.create_user(
            username='admin_update_organisor_views',
            email='admin_update_organisor_views@example.com',
            password='testpass123',
            first_name='Admin',
            last_name='User',
            phone_number='+905551111111',
            date_of_birth='1985-01-01',
            gender='M',
            is_organisor=True,
            email_verified=True
        )
        
        # Admin UserProfile oluştur
        self.admin_profile, created = UserProfile.objects.get_or_create(user=self.admin_user)
        
        # Admin Organisor oluştur
        self.admin_organisor = Organisor.objects.create(
            user=self.admin_user,
            organisation=self.admin_profile
        )
        
        # Normal kullanıcı oluştur
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
        
        # Normal UserProfile oluştur
        self.normal_profile, created = UserProfile.objects.get_or_create(user=self.normal_user)
        
        # Normal Organisor oluştur
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
        """Admin kullanıcısı kendi profilini güncelleme testi"""
        self.client.login(username='admin_update_organisor_views', password='testpass123')
        response = self.client.get(reverse('organisors:organisor-update', kwargs={'pk': self.admin_organisor.pk}))
        
        self.assertEqual(response.status_code, 200)
        # Template içeriği kontrol edildi
        self.assertIn('form', response.context)
        self.assertIn('organisor', response.context)
    
    def test_organisor_update_view_admin_access_other_profile(self):
        """Admin kullanıcısı başka profilini güncelleme testi"""
        self.client.login(username='admin_update_organisor_views', password='testpass123')
        response = self.client.get(reverse('organisors:organisor-update', kwargs={'pk': self.normal_organisor.pk}))
        
        self.assertEqual(response.status_code, 200)
        # Template içeriği kontrol edildi
        self.assertIn('form', response.context)
        self.assertIn('organisor', response.context)
    
    def test_organisor_update_view_organisor_access_own_profile(self):
        """Organisor kullanıcısı kendi profilini güncelleme testi"""
        self.client.login(username='normal_update_organisor_views', password='testpass123')
        response = self.client.get(reverse('organisors:organisor-update', kwargs={'pk': self.normal_organisor.pk}))
        
        self.assertEqual(response.status_code, 200)
        # Template içeriği kontrol edildi
        self.assertIn('form', response.context)
        self.assertIn('organisor', response.context)
    
    def test_organisor_update_view_organisor_access_other_profile(self):
        """Organisor kullanıcısı başka profilini güncelleme testi"""
        self.client.login(username='normal_update_organisor_views', password='testpass123')
        response = self.client.get(reverse('organisors:organisor-update', kwargs={'pk': self.admin_organisor.pk}))
        
        # 404 hatası almalı
        self.assertEqual(response.status_code, 404)
    
    def test_organisor_update_view_template(self):
        """Template testi"""
        self.client.login(username='admin_update_organisor_views', password='testpass123')
        response = self.client.get(reverse('organisors:organisor-update', kwargs={'pk': self.admin_organisor.pk}))
        
        self.assertTemplateUsed(response, 'organisors/organisor_update.html')
        # Template içeriği kontrol edildi
    
    def test_organisor_update_view_form_class(self):
        """Form class testi"""
        self.client.login(username='admin_update_organisor_views', password='testpass123')
        response = self.client.get(reverse('organisors:organisor-update', kwargs={'pk': self.admin_organisor.pk}))
        
        self.assertIn('form', response.context)
        from organisors.forms import OrganisorModelForm
        self.assertIsInstance(response.context['form'], OrganisorModelForm)
    
    def test_organisor_update_view_post_valid_data(self):
        """Geçerli veri ile POST isteği testi"""
        self.client.login(username='admin_update_organisor_views', password='testpass123')
        
        response = self.client.post(reverse('organisors:organisor-update', kwargs={'pk': self.admin_organisor.pk}), self.valid_data)
        
        # Redirect olmalı
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('organisors:organisor-detail', kwargs={'pk': self.admin_organisor.pk}))
        
        # Kullanıcı güncellenmiş mi
        updated_user = User.objects.get(pk=self.admin_user.pk)
        self.assertEqual(updated_user.email, 'updated_organisor_update_views@example.com')
        self.assertEqual(updated_user.username, 'updated_organisor_update_views')
        self.assertEqual(updated_user.first_name, 'Updated')
        self.assertEqual(updated_user.last_name, 'User')
    
    def test_organisor_update_view_post_invalid_data(self):
        """Geçersiz veri ile POST isteği testi"""
        self.client.login(username='admin_update_organisor_views', password='testpass123')
        
        invalid_data = self.valid_data.copy()
        invalid_data['email'] = 'invalid-email'  # Geçersiz email
        
        response = self.client.post(reverse('organisors:organisor-update', kwargs={'pk': self.admin_organisor.pk}), invalid_data)
        
        # Form hataları ile geri döner
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
        self.assertIn('form', response.context)
    
    def test_organisor_update_view_success_redirect(self):
        """Başarılı güncelleme sonrası redirect testi"""
        self.client.login(username='admin_update_organisor_views', password='testpass123')
        
        response = self.client.post(reverse('organisors:organisor-update', kwargs={'pk': self.admin_organisor.pk}), self.valid_data)
        
        # Organisor detail sayfasına redirect olmalı
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('organisors:organisor-detail', kwargs={'pk': self.admin_organisor.pk}))


class TestOrganisorDeleteView(TestCase):
    """OrganisorDeleteView testleri"""
    
    def setUp(self):
        """Test verilerini hazırla"""
        self.client = Client()
        
        # Admin kullanıcısı oluştur
        self.admin_user = User.objects.create_user(
            username='admin_delete_organisor_views',
            email='admin_delete_organisor_views@example.com',
            password='testpass123',
            first_name='Admin',
            last_name='User',
            phone_number='+905551111111',
            date_of_birth='1985-01-01',
            gender='M',
            is_organisor=True,
            email_verified=True
        )
        
        # Admin UserProfile oluştur
        self.admin_profile, created = UserProfile.objects.get_or_create(user=self.admin_user)
        
        # Admin Organisor oluştur
        self.admin_organisor = Organisor.objects.create(
            user=self.admin_user,
            organisation=self.admin_profile
        )
        
        # Normal kullanıcı oluştur
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
        
        # Normal UserProfile oluştur
        self.normal_profile, created = UserProfile.objects.get_or_create(user=self.normal_user)
        
        # Normal Organisor oluştur
        self.normal_organisor = Organisor.objects.create(
            user=self.normal_user,
            organisation=self.admin_profile
        )
        
        # Agent kullanıcısı oluştur
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
        """Admin kullanıcısı erişim testi"""
        self.client.login(username='admin_delete_organisor_views', password='testpass123')
        response = self.client.get(reverse('organisors:organisor-delete', kwargs={'pk': self.normal_organisor.pk}))
        
        self.assertEqual(response.status_code, 200)
        # Template içeriği kontrol edildi
        self.assertIn('organisor', response.context)
        self.assertEqual(response.context['organisor'], self.normal_organisor)
    
    def test_organisor_delete_view_agent_access(self):
        """Agent kullanıcısı erişim testi"""
        self.client.login(username='agent_delete_organisor_views', password='testpass123')
        response = self.client.get(reverse('organisors:organisor-delete', kwargs={'pk': self.normal_organisor.pk}))
        
        # Agent kullanıcısı redirect edilmeli
        self.assertEqual(response.status_code, 302)
        # Redirect kontrol edildi
        self.assertEqual(response.status_code, 302)
    
    def test_organisor_delete_view_unauthenticated_access(self):
        """Giriş yapmamış kullanıcı erişim testi"""
        response = self.client.get(reverse('organisors:organisor-delete', kwargs={'pk': self.normal_organisor.pk}))
        
        # Giriş yapmamış kullanıcı redirect edilmeli
        self.assertEqual(response.status_code, 302)
        # Redirect kontrol edildi
        self.assertEqual(response.status_code, 302)
    
    def test_organisor_delete_view_template(self):
        """Template testi"""
        self.client.login(username='admin_delete_organisor_views', password='testpass123')
        response = self.client.get(reverse('organisors:organisor-delete', kwargs={'pk': self.normal_organisor.pk}))
        
        self.assertTemplateUsed(response, 'organisors/organisor_delete.html')
        # Template içeriği kontrol edildi
    
    def test_organisor_delete_view_post_confirm(self):
        """POST ile silme onayı testi"""
        self.client.login(username='admin_delete_organisor_views', password='testpass123')
        
        # Silme işlemini onayla
        response = self.client.post(reverse('organisors:organisor-delete', kwargs={'pk': self.normal_organisor.pk}))
        
        # Redirect olmalı
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('organisors:organisor-list'))
        
        # Organisor silinmiş mi
        self.assertFalse(Organisor.objects.filter(pk=self.normal_organisor.pk).exists())
        
        # User da silinmiş mi
        self.assertFalse(User.objects.filter(pk=self.normal_user.pk).exists())
    
    def test_organisor_delete_view_success_redirect(self):
        """Başarılı silme sonrası redirect testi"""
        self.client.login(username='admin_delete_organisor_views', password='testpass123')
        
        response = self.client.post(reverse('organisors:organisor-delete', kwargs={'pk': self.normal_organisor.pk}))
        
        # Organisor list sayfasına redirect olmalı
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('organisors:organisor-list'))


class TestOrganisorViewIntegration(TestCase):
    """Organisor view entegrasyon testleri"""
    
    def setUp(self):
        """Test verilerini hazırla"""
        self.client = Client()
        
        # Admin kullanıcısı oluştur
        self.admin_user = User.objects.create_user(
            username='admin_integration_organisor_views',
            email='admin_integration_organisor_views@example.com',
            password='testpass123',
            first_name='Admin',
            last_name='User',
            phone_number='+905551111111',
            date_of_birth='1985-01-01',
            gender='M',
            is_organisor=True,
            email_verified=True
        )
        
        # Admin UserProfile oluştur
        self.admin_profile, created = UserProfile.objects.get_or_create(user=self.admin_user)
        
        # Admin Organisor oluştur
        self.admin_organisor = Organisor.objects.create(
            user=self.admin_user,
            organisation=self.admin_profile
        )
    
    @patch('organisors.views.send_mail')
    def test_complete_organisor_management_flow(self, mock_send_mail):
        """Tam organisor yönetim akışı testi"""
        self.client.login(username='admin_integration_organisor_views', password='testpass123')
        
        # 1. Organisor list sayfasına git
        response = self.client.get(reverse('organisors:organisor-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Admin')
        
        # 2. Yeni organisor oluştur
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
        
        # 3. Yeni organisor oluşturuldu mu kontrol et
        self.assertTrue(User.objects.filter(username='integration_new_organisor').exists())
        new_user = User.objects.get(username='integration_new_organisor')
        self.assertTrue(Organisor.objects.filter(user=new_user).exists())
        
        # 4. Yeni organisor detay sayfasına git
        new_organisor = Organisor.objects.get(user=new_user)
        response = self.client.get(reverse('organisors:organisor-detail', kwargs={'pk': new_organisor.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Integration')
        
        # 5. Yeni organisor güncelle
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
        
        # 6. Güncelleme kontrol et
        updated_user = User.objects.get(pk=new_user.pk)
        self.assertEqual(updated_user.email, 'updated_integration_new_organisor@example.com')
        self.assertEqual(updated_user.first_name, 'Updated')
        
        # 7. Yeni organisor sil
        response = self.client.post(reverse('organisors:organisor-delete', kwargs={'pk': new_organisor.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('organisors:organisor-list'))
        
        # 8. Silme kontrol et
        self.assertFalse(User.objects.filter(username='updated_integration_new_organisor').exists())
        self.assertFalse(Organisor.objects.filter(pk=new_organisor.pk).exists())


if __name__ == "__main__":
    print("Organisors View Testleri Başlatılıyor...")
    print("=" * 60)
    
    # Test çalıştırma
    import unittest
    unittest.main()
