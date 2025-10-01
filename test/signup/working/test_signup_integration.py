"""
Signup Entegrasyon Test Dosyası
Bu dosya signup ile ilgili tüm entegrasyon testlerini içerir.
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

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djcrm.settings')
django.setup()

from leads.models import User, UserProfile, EmailVerificationToken
from organisors.models import Organisor

User = get_user_model()


class TestSignupCompleteFlow(TestCase):
    """Tam signup akışı entegrasyon testleri"""
    
    def setUp(self):
        """Test verilerini hazırla"""
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
        """Tam signup ve doğrulama akışı testi"""
        
        # 1. Signup sayfasına git
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sign Up')
        
        # 2. Signup formunu gönder
        response = self.client.post(reverse('signup'), self.valid_signup_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('verify-email-sent'))
        
        # 3. Kullanıcı oluşturuldu mu kontrol et
        self.assertTrue(User.objects.filter(username='complete_flow_user').exists())
        user = User.objects.get(username='complete_flow_user')
        
        # 4. Kullanıcı özellikleri doğru mu
        self.assertEqual(user.email, 'complete_flow@example.com')
        self.assertEqual(user.first_name, 'Complete')
        self.assertEqual(user.last_name, 'Flow')
        self.assertTrue(user.is_organisor)
        self.assertFalse(user.is_agent)
        self.assertFalse(user.email_verified)
        
        # 5. UserProfile oluşturuldu mu
        self.assertTrue(UserProfile.objects.filter(user=user).exists())
        user_profile = UserProfile.objects.get(user=user)
        
        # 6. Organisor oluşturuldu mu
        self.assertTrue(Organisor.objects.filter(user=user).exists())
        organisor = Organisor.objects.get(user=user)
        self.assertEqual(organisor.organisation, user_profile)
        
        # 7. Email verification token oluşturuldu mu
        self.assertTrue(EmailVerificationToken.objects.filter(user=user).exists())
        verification_token = EmailVerificationToken.objects.get(user=user)
        self.assertFalse(verification_token.is_used)
        self.assertFalse(verification_token.is_expired())
        
        # 8. Email gönderildi mi
        mock_send_mail.assert_called_once()
        
        # 9. Email verification sent sayfasına git
        response = self.client.get(reverse('verify-email-sent'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'verification')
        
        # 10. Email doğrulama linkine tıkla
        response = self.client.get(
            reverse('verify-email', kwargs={'token': verification_token.token})
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))
        
        # 11. Kullanıcı email'i doğrulandı mı
        updated_user = User.objects.get(pk=user.pk)
        self.assertTrue(updated_user.email_verified)
        
        # 12. Token kullanıldı olarak işaretlendi mi
        updated_token = EmailVerificationToken.objects.get(pk=verification_token.pk)
        self.assertTrue(updated_token.is_used)
        
        # 13. Login sayfasına erişim
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')
    
    def test_signup_flow_with_invalid_data(self):
        """Geçersiz verilerle signup akışı testi"""
        
        # Geçersiz email formatı
        invalid_data = self.valid_signup_data.copy()
        invalid_data['email'] = 'invalid-email-format'
        
        response = self.client.post(reverse('signup'), invalid_data)
        self.assertEqual(response.status_code, 200)  # Form hataları ile geri döner
        self.assertFalse(User.objects.filter(username='complete_flow_user').exists())
        
        # Şifre uyumsuzluğu
        invalid_data = self.valid_signup_data.copy()
        invalid_data['password1'] = 'password123!'
        invalid_data['password2'] = 'differentpassword123!'
        
        response = self.client.post(reverse('signup'), invalid_data)
        self.assertEqual(response.status_code, 200)  # Form hataları ile geri döner
        self.assertFalse(User.objects.filter(username='complete_flow_user').exists())
        
        # Eksik zorunlu alanlar
        incomplete_data = {
            'username': 'complete_flow_user',
            'email': 'complete_flow@example.com',
            # Diğer alanlar eksik
        }
        
        response = self.client.post(reverse('signup'), incomplete_data)
        self.assertEqual(response.status_code, 200)  # Form hataları ile geri döner
        self.assertFalse(User.objects.filter(username='complete_flow_user').exists())
    
    def test_signup_flow_with_duplicate_data(self):
        """Çakışan verilerle signup akışı testi"""
        
        # Önce bir kullanıcı oluştur
        User.objects.create_user(
            username='duplicate_user',
            email='duplicate@example.com',
            password='testpass123',
            phone_number='+905551111111'
        )
        
        # Aynı email ile signup
        duplicate_data = self.valid_signup_data.copy()
        duplicate_data['email'] = 'duplicate@example.com'
        
        response = self.client.post(reverse('signup'), duplicate_data)
        self.assertEqual(response.status_code, 200)  # Form hataları ile geri döner
        self.assertFalse(User.objects.filter(username='complete_flow_user').exists())
        
        # Aynı telefon numarası ile signup
        duplicate_data = self.valid_signup_data.copy()
        duplicate_data['phone_number_0'] = '+90'
        duplicate_data['phone_number_1'] = '5551111111'
        
        response = self.client.post(reverse('signup'), duplicate_data)
        self.assertEqual(response.status_code, 200)  # Form hataları ile geri döner
        self.assertFalse(User.objects.filter(username='complete_flow_user').exists())


class TestEmailVerificationFlow(TestCase):
    """Email doğrulama akışı entegrasyon testleri"""
    
    def setUp(self):
        """Test verilerini hazırla"""
        self.client = Client()
        
        # Test kullanıcısı oluştur
        self.user = User.objects.create_user(
            username='verification_flow_user',
            email='verification_flow@example.com',
            password='testpass123!',
            first_name='Verification',
            last_name='Flow',
            is_organisor=True,
            email_verified=False
        )
        
        # İlişkili modelleri oluştur
        # UserProfile signal ile otomatik oluşturulmuş olmalı
        self.user_profile = UserProfile.objects.get(user=self.user)
        self.organisor = Organisor.objects.create(user=self.user, organisation=self.user_profile)
        self.verification_token = EmailVerificationToken.objects.create(user=self.user)
    
    def test_email_verification_success_flow(self):
        """Email doğrulama başarılı akışı testi"""
        
        # 1. Email doğrulama linkine tıkla
        response = self.client.get(
            reverse('verify-email', kwargs={'token': self.verification_token.token})
        )
        
        # 2. Login sayfasına yönlendirilmeli
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))
        
        # 3. Kullanıcı email'i doğrulandı mı
        updated_user = User.objects.get(pk=self.user.pk)
        self.assertTrue(updated_user.email_verified)
        
        # 4. Token kullanıldı olarak işaretlendi mi
        updated_token = EmailVerificationToken.objects.get(pk=self.verification_token.pk)
        self.assertTrue(updated_token.is_used)
    
    def test_email_verification_invalid_token_flow(self):
        """Geçersiz token ile email doğrulama akışı testi"""
        
        # Geçersiz token
        fake_token = '00000000-0000-0000-0000-000000000000'
        
        response = self.client.get(
            reverse('verify-email', kwargs={'token': fake_token})
        )
        
        # Verification failed sayfasına yönlendirilmeli
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('verify-email-failed'))
        
        # Kullanıcı email'i doğrulanmadı mı
        updated_user = User.objects.get(pk=self.user.pk)
        self.assertFalse(updated_user.email_verified)
    
    def test_email_verification_expired_token_flow(self):
        """Süresi dolmuş token ile email doğrulama akışı testi"""
        
        # Token'ı süresi dolmuş olarak işaretle
        expired_time = timezone.now() - timedelta(hours=25)
        self.verification_token.created_at = expired_time
        self.verification_token.save()
        
        response = self.client.get(
            reverse('verify-email', kwargs={'token': self.verification_token.token})
        )
        
        # Verification failed sayfasına yönlendirilmeli
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('verify-email-failed'))
        
        # Kullanıcı email'i doğrulanmadı mı
        updated_user = User.objects.get(pk=self.user.pk)
        self.assertFalse(updated_user.email_verified)
    
    def test_email_verification_used_token_flow(self):
        """Kullanılmış token ile email doğrulama akışı testi"""
        
        # Token'ı kullanılmış olarak işaretle
        self.verification_token.is_used = True
        self.verification_token.save()
        
        response = self.client.get(
            reverse('verify-email', kwargs={'token': self.verification_token.token})
        )
        
        # Verification failed sayfasına yönlendirilmeli
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('verify-email-failed'))
        
        # Kullanıcı email'i doğrulanmadı mı
        updated_user = User.objects.get(pk=self.user.pk)
        self.assertFalse(updated_user.email_verified)


class TestSignupModelRelationships(TestCase):
    """Signup model ilişkileri entegrasyon testleri"""
    
    def setUp(self):
        """Test verilerini hazırla"""
        self.user_data = {
            'username': 'relationship_test_user',
            'email': 'relationship_test@example.com',
            'password': 'testpass123!',
            'first_name': 'Relationship',
            'last_name': 'Test',
            'phone_number': '+905559876543',  # User model için doğru format
            'date_of_birth': datetime(1985, 5, 15).date(),
            'gender': 'F',
            'is_organisor': True,
            'email_verified': False,
        }
    
    def test_signup_model_creation_and_relationships(self):
        """Signup model oluşturma ve ilişkiler testi"""
        
        # 1. User oluştur
        user = User.objects.create_user(**self.user_data)
        
        # 2. UserProfile signal ile otomatik oluşturulmuş olmalı
        user_profile = UserProfile.objects.get(user=user)
        
        # 3. Organisor oluştur
        organisor = Organisor.objects.create(user=user, organisation=user_profile)
        
        # 4. EmailVerificationToken oluştur
        verification_token = EmailVerificationToken.objects.create(user=user)
        
        # Model sayıları kontrol et
        self.assertEqual(User.objects.filter(username='relationship_test_user').count(), 1)
        self.assertEqual(UserProfile.objects.filter(user=user).count(), 1)
        self.assertEqual(Organisor.objects.filter(user=user).count(), 1)
        self.assertEqual(EmailVerificationToken.objects.filter(user=user).count(), 1)
        
        # İlişkiler kontrol et
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
        """Signup model veri tutarlılığı testi"""
        
        # Tam signup süreci
        user = User.objects.create_user(**self.user_data)
        user_profile = UserProfile.objects.get(user=user)
        organisor = Organisor.objects.create(user=user, organisation=user_profile)
        verification_token = EmailVerificationToken.objects.create(user=user)
        
        # Veri tutarlılığı kontrolü
        self.assertEqual(user.is_organisor, True)
        self.assertEqual(user.email_verified, False)
        self.assertEqual(user.userprofile, user_profile)
        self.assertEqual(user.organisor, organisor)
        self.assertEqual(organisor.organisation, user_profile)
        self.assertEqual(verification_token.user, user)
        self.assertFalse(verification_token.is_used)
        self.assertFalse(verification_token.is_expired())
        
        # Email doğrulama sonrası
        user.email_verified = True
        user.save()
        verification_token.is_used = True
        verification_token.save()
        
        updated_user = User.objects.get(pk=user.pk)
        updated_token = EmailVerificationToken.objects.get(pk=verification_token.pk)
        
        self.assertTrue(updated_user.email_verified)
        self.assertTrue(updated_token.is_used)


class TestSignupFormIntegration(TestCase):
    """Signup form entegrasyon testleri"""
    
    def setUp(self):
        """Test verilerini hazırla"""
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
        """Form save ve model oluşturma entegrasyonu testi"""
        
        from leads.forms import CustomUserCreationForm
        
        # Form oluştur ve kaydet
        form = CustomUserCreationForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
        
        user = form.save()
        
        # Kullanıcı veritabanında oluşturuldu mu
        self.assertTrue(User.objects.filter(username='form_integration_user').exists())
        
        saved_user = User.objects.get(username='form_integration_user')
        self.assertEqual(saved_user.email, 'form_integration@example.com')
        self.assertEqual(saved_user.first_name, 'Form')
        self.assertEqual(saved_user.last_name, 'Integration')
        self.assertEqual(saved_user.phone_number, '+905551111111')
        self.assertEqual(saved_user.gender, 'M')
        self.assertEqual(saved_user.date_of_birth.strftime('%Y-%m-%d'), '1992-03-15')
        
        # Şifre doğru set edildi mi
        self.assertTrue(saved_user.check_password('formpass123!'))
    
    def test_form_validation_with_existing_data(self):
        """Mevcut verilerle form validasyon entegrasyonu testi"""
        
        from leads.forms import CustomUserCreationForm
        
        # Önce bir kullanıcı oluştur
        User.objects.create_user(
            username='existing_form_user',
            email='existing_form@example.com',
            password='testpass123',
            phone_number='+905552222222'
        )
        
        # Çakışan email ile form test et
        data = self.valid_data.copy()
        data['email'] = 'existing_form@example.com'
        data['username'] = 'different_username'
        
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        
        # Çakışan telefon numarası ile form test et
        data = self.valid_data.copy()
        data['phone_number_0'] = '+90'
        data['phone_number_1'] = '5552222222'
        data['username'] = 'different_username2'
        
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('phone_number', form.errors)
        
        # Çakışan kullanıcı adı ile form test et
        data = self.valid_data.copy()
        data['username'] = 'existing_form_user'
        
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)


class TestSignupViewFormIntegration(TestCase):
    """Signup view ve form entegrasyon testleri"""
    
    def setUp(self):
        """Test verilerini hazırla"""
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
        """Signup view ve form entegrasyonu testi"""
        
        # 1. Signup sayfasına git
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        
        # Form class kontrol et
        from leads.forms import CustomUserCreationForm
        self.assertIsInstance(response.context['form'], CustomUserCreationForm)
        
        # 2. Form gönder
        response = self.client.post(reverse('signup'), self.valid_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('verify-email-sent'))
        
        # 3. Kullanıcı oluşturuldu mu
        self.assertTrue(User.objects.filter(username='view_form_integration_user').exists())
        user = User.objects.get(username='view_form_integration_user')
        
        # 4. Kullanıcı özellikleri doğru mu
        self.assertEqual(user.email, 'view_form_integration@example.com')
        self.assertEqual(user.first_name, 'View')
        self.assertEqual(user.last_name, 'Form')
        self.assertTrue(user.is_organisor)
        self.assertFalse(user.is_agent)
        self.assertFalse(user.email_verified)
        
        # 5. İlişkili modeller oluşturuldu mu
        self.assertTrue(UserProfile.objects.filter(user=user).exists())
        self.assertTrue(Organisor.objects.filter(user=user).exists())
        self.assertTrue(EmailVerificationToken.objects.filter(user=user).exists())
        
        # 6. Email gönderildi mi
        mock_send_mail.assert_called_once()
    
    def test_signup_view_form_validation_integration(self):
        """Signup view form validasyon entegrasyonu testi"""
        
        # Geçersiz veri ile form gönder
        invalid_data = self.valid_data.copy()
        invalid_data['email'] = 'invalid-email-format'
        
        response = self.client.post(reverse('signup'), invalid_data)
        self.assertEqual(response.status_code, 200)  # Form hataları ile geri döner
        
        # Kullanıcı oluşturulmadı mı
        self.assertFalse(User.objects.filter(username='view_form_integration_user').exists())
        
        # Form hataları context'te var mı
        self.assertIn('form', response.context)
        self.assertFalse(response.context['form'].is_valid())


if __name__ == "__main__":
    print("Signup Entegrasyon Testleri Başlatılıyor...")
    print("=" * 60)
    
    # Test çalıştırma
    import unittest
    unittest.main()
