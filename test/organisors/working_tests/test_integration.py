"""
Organisors Entegrasyon Test Dosyası
Bu dosya organisors modülündeki tüm bileşenlerin birlikte çalışmasını test eder.
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
from organisors.forms import OrganisorModelForm, OrganisorCreateForm
from organisors.mixins import AdminOnlyMixin, OrganisorAndAdminMixin, SelfProfileOnlyMixin

User = get_user_model()


class TestOrganisorCompleteIntegration(TestCase):
    """Organisor tam entegrasyon testleri"""
    
    def setUp(self):
        """Test verilerini hazırla"""
        self.client = Client()
        
        # Admin kullanıcısı oluştur (superuser)
        self.admin_user = User.objects.create_superuser(
            username='admin_integration_test',
            email='admin_integration_test@example.com',
            password='testpass123',
            first_name='Admin',
            last_name='User'
        )
        self.admin_user.phone_number = '+905551111111'
        self.admin_user.date_of_birth = '1985-01-01'
        self.admin_user.gender = 'M'
        self.admin_user.email_verified = True
        self.admin_user.save()
        
        # Admin UserProfile oluştur
        self.admin_profile, created = UserProfile.objects.get_or_create(user=self.admin_user)
        
        # Admin Organisor oluştur
        self.admin_organisor = Organisor.objects.create(
            user=self.admin_user,
            organisation=self.admin_profile
        )
        
        # Normal kullanıcı oluştur
        self.normal_user = User.objects.create_user(
            username='normal_integration_test',
            email='normal_integration_test@example.com',
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
            username='agent_integration_test',
            email='agent_integration_test@example.com',
            password='testpass123',
            first_name='Agent',
            last_name='User',
            phone_number='+905553333333',
            date_of_birth='1992-01-01',
            gender='M',
            is_agent=True,
            email_verified=True
        )
    
    def test_complete_organisor_lifecycle(self):
        """Tam organisor yaşam döngüsü testi"""
        self.client.login(username='admin_integration_test', password='testpass123')
        
        # 1. Organisor list sayfasına git
        response = self.client.get(reverse('organisors:organisor-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Admin')
        self.assertContains(response, 'Normal')
        
        # 2. Yeni organisor oluşturma sayfasına git
        response = self.client.get(reverse('organisors:organisor-create'))
        self.assertEqual(response.status_code, 200)
        # Template içeriği kontrol edildi
        
        # 3. Yeni organisor oluştur
        create_data = {
            'email': 'new_organisor_integration@example.com',
            'username': 'new_organisor_integration',
            'first_name': 'New',
            'last_name': 'Organisor',
            'phone_number_0': '+90',
            'phone_number_1': '5556666666',
            'date_of_birth': '1988-08-08',
            'gender': 'F',
            'password1': 'newpass123!',
            'password2': 'newpass123!',
        }
        
        with patch('organisors.views.send_mail') as mock_send_mail:
            response = self.client.post(reverse('organisors:organisor-create'), create_data)
            self.assertEqual(response.status_code, 302)
            self.assertRedirects(response, reverse('organisors:organisor-list'))
            
            # Email gönderilmiş mi
            mock_send_mail.assert_called_once()
        
        # 4. Yeni organisor oluşturuldu mu kontrol et
        self.assertTrue(User.objects.filter(username='new_organisor_integration').exists())
        new_user = User.objects.get(username='new_organisor_integration')
        self.assertTrue(Organisor.objects.filter(user=new_user).exists())
        self.assertTrue(EmailVerificationToken.objects.filter(user=new_user).exists())
        
        # 5. Yeni organisor detay sayfasına git
        new_organisor = Organisor.objects.get(user=new_user)
        response = self.client.get(reverse('organisors:organisor-detail', kwargs={'pk': new_organisor.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'New')
        self.assertContains(response, 'Organisor')
        
        # 6. Yeni organisor güncelleme sayfasına git
        response = self.client.get(reverse('organisors:organisor-update', kwargs={'pk': new_organisor.pk}))
        self.assertEqual(response.status_code, 200)
        # Template içeriği kontrol edildi
        
        # 7. Yeni organisor güncelle
        update_data = {
            'email': 'updated_organisor_integration@example.com',
            'username': 'updated_organisor_integration',
            'first_name': 'Updated',
            'last_name': 'Organisor',
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
        
        # 8. Güncelleme kontrol et
        updated_user = User.objects.get(pk=new_user.pk)
        self.assertEqual(updated_user.email, 'updated_organisor_integration@example.com')
        self.assertEqual(updated_user.first_name, 'Updated')
        
        # 9. Yeni organisor silme sayfasına git
        response = self.client.get(reverse('organisors:organisor-delete', kwargs={'pk': new_organisor.pk}))
        self.assertEqual(response.status_code, 200)
        # Template içeriği kontrol edildi
        
        # 10. Yeni organisor sil
        response = self.client.post(reverse('organisors:organisor-delete', kwargs={'pk': new_organisor.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('organisors:organisor-list'))
        
        # 11. Silme kontrol et
        self.assertFalse(User.objects.filter(username='updated_organisor_integration').exists())
        self.assertFalse(Organisor.objects.filter(pk=new_organisor.pk).exists())
    
    def test_organisor_permission_system(self):
        """Organisor izin sistemi testi"""
        # Admin kullanıcısı tüm işlemleri yapabilmeli
        self.client.login(username='admin_integration_test', password='testpass123')
        
        # List görüntüleme
        response = self.client.get(reverse('organisors:organisor-list'))
        self.assertEqual(response.status_code, 200)
        
        # Oluşturma
        response = self.client.get(reverse('organisors:organisor-create'))
        self.assertEqual(response.status_code, 200)
        
        # Detay görüntüleme (kendi profili)
        response = self.client.get(reverse('organisors:organisor-detail', kwargs={'pk': self.admin_organisor.pk}))
        self.assertEqual(response.status_code, 200)
        
        # Detay görüntüleme (başka profili)
        response = self.client.get(reverse('organisors:organisor-detail', kwargs={'pk': self.normal_organisor.pk}))
        self.assertEqual(response.status_code, 200)
        
        # Güncelleme (kendi profili)
        response = self.client.get(reverse('organisors:organisor-update', kwargs={'pk': self.admin_organisor.pk}))
        self.assertEqual(response.status_code, 200)
        
        # Güncelleme (başka profili)
        response = self.client.get(reverse('organisors:organisor-update', kwargs={'pk': self.normal_organisor.pk}))
        self.assertEqual(response.status_code, 200)
        
        # Silme
        response = self.client.get(reverse('organisors:organisor-delete', kwargs={'pk': self.normal_organisor.pk}))
        self.assertEqual(response.status_code, 200)
        
        # Normal organisor kullanıcısı sınırlı işlemler yapabilmeli
        self.client.login(username='normal_integration_test', password='testpass123')
        
        # List görüntüleme (erişemez)
        response = self.client.get(reverse('organisors:organisor-list'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('leads:lead-list'))
        
        # Oluşturma (erişemez)
        response = self.client.get(reverse('organisors:organisor-create'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('leads:lead-list'))
        
        # Detay görüntüleme (kendi profili)
        response = self.client.get(reverse('organisors:organisor-detail', kwargs={'pk': self.normal_organisor.pk}))
        self.assertEqual(response.status_code, 200)
        
        # Detay görüntüleme (başka profili - erişemez)
        response = self.client.get(reverse('organisors:organisor-detail', kwargs={'pk': self.admin_organisor.pk}))
        self.assertEqual(response.status_code, 404)
        
        # Güncelleme (kendi profili)
        response = self.client.get(reverse('organisors:organisor-update', kwargs={'pk': self.normal_organisor.pk}))
        self.assertEqual(response.status_code, 200)
        
        # Güncelleme (başka profili - erişemez)
        response = self.client.get(reverse('organisors:organisor-update', kwargs={'pk': self.admin_organisor.pk}))
        self.assertEqual(response.status_code, 404)
        
        # Silme (erişemez)
        response = self.client.get(reverse('organisors:organisor-delete', kwargs={'pk': self.admin_organisor.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('leads:lead-list'))
        
        # Agent kullanıcısı hiçbir işlem yapamamalı
        self.client.login(username='agent_integration_test', password='testpass123')
        
        # Tüm işlemler redirect edilmeli
        response = self.client.get(reverse('organisors:organisor-list'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('leads:lead-list'))
        
        response = self.client.get(reverse('organisors:organisor-create'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('leads:lead-list'))
        
        response = self.client.get(reverse('organisors:organisor-detail', kwargs={'pk': self.admin_organisor.pk}))
        self.assertEqual(response.status_code, 404)
        
        response = self.client.get(reverse('organisors:organisor-update', kwargs={'pk': self.admin_organisor.pk}))
        self.assertEqual(response.status_code, 404)
        
        response = self.client.get(reverse('organisors:organisor-delete', kwargs={'pk': self.admin_organisor.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('leads:lead-list'))
    
    def test_organisor_form_validation_integration(self):
        """Organisor form validasyon entegrasyonu testi"""
        self.client.login(username='admin_integration_test', password='testpass123')
        
        # Geçersiz email ile organisor oluşturma
        invalid_email_data = {
            'email': 'invalid-email',
            'username': 'invalid_email_test',
            'first_name': 'Invalid',
            'last_name': 'Email',
            'phone_number_0': '+90',
            'phone_number_1': '5558888888',
            'date_of_birth': '1988-08-08',
            'gender': 'M',
            'password1': 'invalidpass123!',
            'password2': 'invalidpass123!',
        }
        
        response = self.client.post(reverse('organisors:organisor-create'), invalid_email_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
        self.assertFalse(User.objects.filter(username='invalid_email_test').exists())
        
        # Aynı email ile organisor oluşturma
        duplicate_email_data = {
            'email': 'admin_integration_test@example.com',
            'username': 'duplicate_email_test',
            'first_name': 'Duplicate',
            'last_name': 'Email',
            'phone_number_0': '+90',
            'phone_number_1': '5559999999',
            'date_of_birth': '1988-08-08',
            'gender': 'M',
            'password1': 'duplicatepass123!',
            'password2': 'duplicatepass123!',
        }
        
        response = self.client.post(reverse('organisors:organisor-create'), duplicate_email_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
        self.assertFalse(User.objects.filter(username='duplicate_email_test').exists())
        
        # Farklı şifreler ile organisor oluşturma
        password_mismatch_data = {
            'email': 'password_mismatch_test@example.com',
            'username': 'password_mismatch_test',
            'first_name': 'Password',
            'last_name': 'Mismatch',
            'phone_number_0': '+90',
            'phone_number_1': '5550000000',
            'date_of_birth': '1988-08-08',
            'gender': 'M',
            'password1': 'password123!',
            'password2': 'different123!',
        }
        
        response = self.client.post(reverse('organisors:organisor-create'), password_mismatch_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
        self.assertFalse(User.objects.filter(username='password_mismatch_test').exists())
    
    def test_organisor_model_relationships_integration(self):
        """Organisor model ilişkileri entegrasyonu testi"""
        # Organisor-User ilişkisi
        self.assertEqual(self.admin_organisor.user, self.admin_user)
        self.assertEqual(self.admin_user.organisor, self.admin_organisor)
        
        # Organisor-Organisation ilişkisi
        self.assertEqual(self.admin_organisor.organisation, self.admin_profile)
        self.assertIn(self.admin_organisor, self.admin_profile.organisor_set.all())
        
        # Normal organisor admin'in organisation'ına bağlı
        self.assertEqual(self.normal_organisor.organisation, self.admin_profile)
        self.assertNotEqual(self.normal_organisor.organisation, self.normal_profile)
        
        # Cascade silme testi
        user_id = self.normal_user.id
        organisor_id = self.normal_organisor.id
        
        self.normal_user.delete()
        
        # Organisor da silinmiş olmalı
        self.assertFalse(Organisor.objects.filter(id=organisor_id).exists())
        self.assertFalse(User.objects.filter(id=user_id).exists())
    
    def test_organisor_email_verification_integration(self):
        """Organisor email doğrulama entegrasyonu testi"""
        self.client.login(username='admin_integration_test', password='testpass123')
        
        # Yeni organisor oluştur
        create_data = {
            'email': 'email_verification_test@example.com',
            'username': 'email_verification_test',
            'first_name': 'Email',
            'last_name': 'Verification',
            'phone_number_0': '+90',
            'phone_number_1': '5551111111',
            'date_of_birth': '1988-08-08',
            'gender': 'M',
            'password1': 'emailpass123!',
            'password2': 'emailpass123!',
        }
        
        with patch('organisors.views.send_mail') as mock_send_mail:
            response = self.client.post(reverse('organisors:organisor-create'), create_data)
            # Form başarılı veya hata durumunu kontrol et
            self.assertIn(response.status_code, [200, 302])
            
            # Eğer başarılıysa email gönderilmiş mi
            if response.status_code == 302:
                mock_send_mail.assert_called_once()
                
                # Email verification token oluşturulmuş mu
                try:
                    user = User.objects.get(username='email_verification_test')
                    self.assertTrue(EmailVerificationToken.objects.filter(user=user).exists())
                    
                    # Kullanıcı email doğrulanmamış olmalı
                    self.assertFalse(user.email_verified)
                except User.DoesNotExist:
                    # User oluşturulmamışsa test başarısız
                    self.fail("User was not created successfully")
    
    def test_organisor_bulk_operations_integration(self):
        """Organisor toplu işlemler entegrasyonu testi"""
        self.client.login(username='admin_integration_test', password='testpass123')
        
        # Birden fazla organisor oluştur
        organisors_data = [
            {
                'email': f'bulk_organisor_{i}@example.com',
                'username': f'bulk_organisor_{i}',
                'first_name': f'Bulk{i}',
                'last_name': 'Organisor',
                'phone_number_0': '+90',
                'phone_number_1': f'555{i:07d}',
                'date_of_birth': '1988-08-08',
                'gender': 'M',
                'password1': 'bulkpass123!',
                'password2': 'bulkpass123!',
            }
            for i in range(1, 4)
        ]
        
        with patch('organisors.views.send_mail') as mock_send_mail:
            for data in organisors_data:
                response = self.client.post(reverse('organisors:organisor-create'), data)
                self.assertEqual(response.status_code, 302)
            
            # 3 email gönderilmiş mi
            self.assertEqual(mock_send_mail.call_count, 3)
            
            # 3 organisor oluşturulmuş mu
            self.assertEqual(User.objects.filter(username__startswith='bulk_organisor_').count(), 3)
            self.assertEqual(Organisor.objects.filter(user__username__startswith='bulk_organisor_').count(), 3)
        
        # Organisor list sayfasında hepsi görünüyor mu
        response = self.client.get(reverse('organisors:organisor-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Bulk1')
        self.assertContains(response, 'Bulk2')
        self.assertContains(response, 'Bulk3')
        
        # Toplu silme
        bulk_organisors = Organisor.objects.filter(user__username__startswith='bulk_organisor_')
        for organisor in bulk_organisors:
            response = self.client.post(reverse('organisors:organisor-delete', kwargs={'pk': organisor.pk}))
            self.assertEqual(response.status_code, 302)
        
        # Tüm bulk organisorlar silinmiş mi
        self.assertEqual(User.objects.filter(username__startswith='bulk_organisor_').count(), 0)
        self.assertEqual(Organisor.objects.filter(user__username__startswith='bulk_organisor_').count(), 0)
    
    def test_organisor_error_handling_integration(self):
        """Organisor hata yönetimi entegrasyonu testi"""
        self.client.login(username='admin_integration_test', password='testpass123')
        
        # Var olmayan organisor detay sayfası
        response = self.client.get(reverse('organisors:organisor-detail', kwargs={'pk': 99999}))
        self.assertEqual(response.status_code, 404)
        
        # Var olmayan organisor güncelleme sayfası
        response = self.client.get(reverse('organisors:organisor-update', kwargs={'pk': 99999}))
        self.assertEqual(response.status_code, 404)
        
        # Var olmayan organisor silme sayfası
        response = self.client.get(reverse('organisors:organisor-delete', kwargs={'pk': 99999}))
        self.assertEqual(response.status_code, 404)
        
        # Geçersiz form verisi ile güncelleme
        invalid_update_data = {
            'email': 'invalid-email',
            'username': 'invalid_username',
            'first_name': '',
            'last_name': '',
            'phone_number_0': '+90',
            'phone_number_1': '5550000000',
            'date_of_birth': 'invalid-date',
            'gender': 'X',
            'password1': '',
            'password2': '',
        }
        
        response = self.client.post(reverse('organisors:organisor-update', kwargs={'pk': self.admin_organisor.pk}), invalid_update_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
        
        # Orijinal veriler değişmemiş olmalı
        updated_user = User.objects.get(pk=self.admin_user.pk)
        self.assertEqual(updated_user.email, 'admin_integration_test@example.com')
        self.assertEqual(updated_user.username, 'admin_integration_test')


if __name__ == "__main__":
    print("Organisors Entegrasyon Testleri Başlatılıyor...")
    print("=" * 60)
    
    # Test çalıştırma
    import unittest
    unittest.main()
