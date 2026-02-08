"""
Signup Viewları Test Dosyası
Bu dosya signup ile ilgili tüm viewları test eder.
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


class TestSignupView(TestCase):
    """SignupView testleri"""
    
    def setUp(self):
        """Test verilerini hazırla"""
        self.client = Client()
        
        self.valid_data = {
            'username': 'testuser_signup_views',
            'email': 'test_signup_views@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'phone_number_0': '+90',
            'phone_number_1': '5551234567',
            'date_of_birth': '1990-01-01',
            'gender': 'M',
            'password1': 'testpass123!',
            'password2': 'testpass123!',
        }
    
    def test_signup_view_get(self):
        """Signup sayfası GET isteği testi"""
        response = self.client.get(reverse('signup'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sign Up')
        self.assertContains(response, 'form')
        # CSRF token form içinde olmalı
        self.assertContains(response, 'csrfmiddlewaretoken')
    
    @patch('leads.views.send_mail')
    def test_signup_view_post_valid_data(self, mock_send_mail):
        """Signup POST isteği geçerli veri testi"""
        response = self.client.post(reverse('signup'), self.valid_data)
        
        # Redirect olmalı
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('verify-email-sent'))
        
        # Kullanıcı oluşturuldu mu
        self.assertTrue(User.objects.filter(username='testuser_signup_views').exists())
        
        user = User.objects.get(username='testuser_signup_views')
        
        # Kullanıcı özellikleri doğru mu
        self.assertEqual(user.email, 'test_signup_views@example.com')
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User')
        self.assertEqual(user.phone_number, '+905551234567')
        self.assertEqual(user.gender, 'M')
        self.assertEqual(user.date_of_birth.strftime('%Y-%m-%d'), '1990-01-01')
        self.assertTrue(user.is_organisor)
        self.assertFalse(user.is_agent)
        self.assertFalse(user.email_verified)
        
        # UserProfile oluşturuldu mu
        self.assertTrue(UserProfile.objects.filter(user=user).exists())
        
        # Organisor oluşturuldu mu
        self.assertTrue(Organisor.objects.filter(user=user).exists())
        
        # Email verification token oluşturuldu mu
        self.assertTrue(EmailVerificationToken.objects.filter(user=user).exists())
        
        # Email gönderildi mi
        mock_send_mail.assert_called_once()
    
    def test_signup_view_post_invalid_data(self):
        """Signup POST isteği geçersiz veri testi"""
        invalid_data = self.valid_data.copy()
        invalid_data['email'] = 'invalid-email'  # Geçersiz email
        
        response = self.client.post(reverse('signup'), invalid_data)
        
        # Form hataları ile geri döner
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
        
        # Kullanıcı oluşturulmadı mı
        self.assertFalse(User.objects.filter(username='testuser_signup_views').exists())
    
    def test_signup_view_duplicate_email(self):
        """Aynı email ile kayıt testi"""
        # Önce bir kullanıcı oluştur
        User.objects.create_user(
            username='existing_user',
            email='existing@example.com',
            password='testpass123'
        )
        
        # Aynı email ile kayıt olmaya çalış
        data = self.valid_data.copy()
        data['email'] = 'existing@example.com'
        data['username'] = 'different_username'
        
        response = self.client.post(reverse('signup'), data)
        
        # Form hataları ile geri döner
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
        
        # Yeni kullanıcı oluşturulmadı mı
        self.assertFalse(User.objects.filter(username='different_username').exists())
    
    def test_signup_view_duplicate_username(self):
        """Aynı kullanıcı adı ile kayıt testi"""
        # Önce bir kullanıcı oluştur
        User.objects.create_user(
            username='existing_user',
            email='existing@example.com',
            password='testpass123'
        )
        
        # Aynı kullanıcı adı ile kayıt olmaya çalış
        data = self.valid_data.copy()
        data['username'] = 'existing_user'
        data['email'] = 'different@example.com'
        
        response = self.client.post(reverse('signup'), data)
        
        # Form hataları ile geri döner
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
        
        # Yeni kullanıcı oluşturulmadı mı
        self.assertFalse(User.objects.filter(email='different@example.com').exists())
    
    def test_signup_view_password_mismatch(self):
        """Şifre uyumsuzluğu testi"""
        data = self.valid_data.copy()
        data['password1'] = 'password123!'
        data['password2'] = 'differentpassword123!'
        
        response = self.client.post(reverse('signup'), data)
        
        # Form hataları ile geri döner
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
        
        # Kullanıcı oluşturulmadı mı
        self.assertFalse(User.objects.filter(username='testuser_signup_views').exists())
    
    @patch('leads.views.send_mail')
    def test_signup_view_email_sending(self, mock_send_mail):
        """Email gönderimi testi"""
        response = self.client.post(reverse('signup'), self.valid_data)
        
        # Email gönderildi mi
        mock_send_mail.assert_called_once()
        
        # Email içeriği doğru mu
        call_args = mock_send_mail.call_args
        # send_mail positional args: subject, message, from_email, recipient_list
        self.assertEqual(call_args[0][0], 'Darkenyas CRM - Email Verification')  # subject
        self.assertIn('test_signup_views@example.com', call_args[0][3])  # recipient_list
        self.assertIn('Test', call_args[0][1])  # message - First name
        self.assertIn('verify-email', call_args[0][1])  # message - Verification link
    
    def test_signup_view_template(self):
        """Template testi"""
        response = self.client.get(reverse('signup'))
        
        self.assertTemplateUsed(response, 'registration/signup.html')
        self.assertContains(response, 'Sign Up')
        self.assertContains(response, 'Create your account')
        self.assertContains(response, 'Already have an account?')
    
    def test_signup_view_form_class(self):
        """Form class testi"""
        response = self.client.get(reverse('signup'))
        
        self.assertIn('form', response.context)
        from leads.forms import CustomUserCreationForm
        self.assertIsInstance(response.context['form'], CustomUserCreationForm)
    
    def test_signup_view_success_url(self):
        """Success URL testi"""
        with patch('leads.views.send_mail'):
            response = self.client.post(reverse('signup'), self.valid_data)
            self.assertRedirects(response, reverse('verify-email-sent'))


class TestEmailVerificationSentView(TestCase):
    """EmailVerificationSentView testleri"""
    
    def setUp(self):
        """Test verilerini hazırla"""
        self.client = Client()
    
    def test_email_verification_sent_view_get(self):
        """Email verification sent sayfası GET isteği testi"""
        response = self.client.get(reverse('verify-email-sent'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/verify_email_sent.html')
    
    def test_email_verification_sent_view_content(self):
        """Email verification sent sayfası içeriği testi"""
        response = self.client.get(reverse('verify-email-sent'))
        
        self.assertContains(response, 'verification')
        self.assertContains(response, 'email')


class TestEmailVerificationView(TestCase):
    """EmailVerificationView testleri"""
    
    def setUp(self):
        """Test verilerini hazırla"""
        self.client = Client()
        
        # Test kullanıcısı oluştur
        self.user = User.objects.create_user(
            username='verification_test_user',
            email='verification_test@example.com',
            password='testpass123',
            first_name='Verification',
            last_name='Test',
            is_organisor=True,
            email_verified=False
        )
        
        # Email verification token oluştur
        self.verification_token = EmailVerificationToken.objects.create(
            user=self.user
        )
    
    def test_email_verification_valid_token(self):
        """Geçerli token ile email doğrulama testi"""
        response = self.client.get(
            reverse('verify-email', kwargs={'token': self.verification_token.token})
        )
        
        # Verification success sayfasına yönlendirilmeli
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('verify-email-success'))
        
        # Kullanıcı email'i doğrulandı mı
        updated_user = User.objects.get(pk=self.user.pk)
        self.assertTrue(updated_user.email_verified)
        
        # Token kullanıldı olarak işaretlendi mi
        updated_token = EmailVerificationToken.objects.get(pk=self.verification_token.pk)
        self.assertTrue(updated_token.is_used)
    
    def test_email_verification_invalid_token(self):
        """Geçersiz token ile email doğrulama testi"""
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
    
    def test_email_verification_used_token(self):
        """Kullanılmış token ile email doğrulama testi"""
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
    
    def test_email_verification_expired_token(self):
        """Süresi dolmuş token ile email doğrulama testi"""
        # Token'ı 25 saat önce oluştur (24 saatlik süre dolmuş)
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
    
    def test_email_verification_already_verified(self):
        """Zaten doğrulanmış email testi"""
        # Kullanıcıyı zaten doğrulanmış olarak işaretle
        self.user.email_verified = True
        self.user.save()
        
        response = self.client.get(
            reverse('verify-email', kwargs={'token': self.verification_token.token})
        )
        
        # Yine de doğrulama işlemi gerçekleşmeli (token kullanılmış olarak işaretlenir)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('verify-email-success'))
        
        # Token kullanıldı olarak işaretlendi mi
        updated_token = EmailVerificationToken.objects.get(pk=self.verification_token.pk)
        self.assertTrue(updated_token.is_used)


class TestEmailVerificationFailedView(TestCase):
    """EmailVerificationFailedView testleri"""
    
    def setUp(self):
        """Test verilerini hazırla"""
        self.client = Client()
    
    def test_email_verification_failed_view_get(self):
        """Email verification failed sayfası GET isteği testi"""
        response = self.client.get(reverse('verify-email-failed'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/verify_email_failed.html')
    
    def test_email_verification_failed_view_content(self):
        """Email verification failed sayfası içeriği testi"""
        response = self.client.get(reverse('verify-email-failed'))
        
        self.assertContains(response, 'verification')
        # Template içeriği kontrol et
        self.assertContains(response, 'verification')


class TestSignupIntegration(TestCase):
    """Signup entegrasyon testleri"""
    
    def setUp(self):
        """Test verilerini hazırla"""
        self.client = Client()
        
        self.valid_data = {
            'username': 'integration_test_user',
            'email': 'integration_test@example.com',
            'first_name': 'Integration',
            'last_name': 'Test',
            'phone_number_0': '+90',
            'phone_number_1': '5559876543',
            'date_of_birth': '1985-05-15',
            'gender': 'F',
            'password1': 'testpass123!',
            'password2': 'testpass123!',
        }
    
    @patch('leads.views.send_mail')
    def test_complete_signup_flow(self, mock_send_mail):
        """Tam signup akışı testi"""
        # 1. Signup sayfasına git
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        
        # 2. Form gönder
        response = self.client.post(reverse('signup'), self.valid_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('verify-email-sent'))
        
        # 3. Email verification sent sayfasına git
        response = self.client.get(reverse('verify-email-sent'))
        self.assertEqual(response.status_code, 200)
        
        # 4. Kullanıcı oluşturuldu mu kontrol et
        user = User.objects.get(username='integration_test_user')
        self.assertFalse(user.email_verified)
        
        # 5. Email verification token oluşturuldu mu
        verification_token = EmailVerificationToken.objects.get(user=user)
        self.assertFalse(verification_token.is_used)
        
        # 6. Email doğrulama linkine tıkla
        response = self.client.get(
            reverse('verify-email', kwargs={'token': verification_token.token})
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('verify-email-success'))
        
        # 7. Kullanıcı email'i doğrulandı mı
        updated_user = User.objects.get(pk=user.pk)
        self.assertTrue(updated_user.email_verified)
        
        # 8. Token kullanıldı olarak işaretlendi mi
        updated_token = EmailVerificationToken.objects.get(pk=verification_token.pk)
        self.assertTrue(updated_token.is_used)
        
        # 9. Email gönderildi mi
        mock_send_mail.assert_called_once()
    
    def test_signup_with_duplicate_data(self):
        """Çakışan verilerle signup testi"""
        # Önce bir kullanıcı oluştur
        User.objects.create_user(
            username='duplicate_user',
            email='duplicate@example.com',
            password='testpass123',
            phone_number='+905551111111'
        )
        
        # Aynı email ile signup olmaya çalış
        data = self.valid_data.copy()
        data['email'] = 'duplicate@example.com'
        
        response = self.client.post(reverse('signup'), data)
        self.assertEqual(response.status_code, 200)  # Form hataları ile geri döner
        self.assertFalse(User.objects.filter(username='integration_test_user').exists())
        
        # Aynı telefon numarası ile signup olmaya çalış
        data = self.valid_data.copy()
        data['phone_number_0'] = '+90'
        data['phone_number_1'] = '5551111111'
        
        response = self.client.post(reverse('signup'), data)
        self.assertEqual(response.status_code, 200)  # Form hataları ile geri döner
        self.assertFalse(User.objects.filter(username='integration_test_user').exists())
    
    def test_signup_form_validation(self):
        """Signup form validasyon testi"""
        # Eksik alanlar
        incomplete_data = {
            'username': 'test_user',
            'email': 'test@example.com',
            # Diğer alanlar eksik
        }
        
        response = self.client.post(reverse('signup'), incomplete_data)
        self.assertEqual(response.status_code, 200)  # Form hataları ile geri döner
        self.assertFalse(User.objects.filter(username='test_user').exists())
        
        # Geçersiz email formatı
        invalid_email_data = self.valid_data.copy()
        invalid_email_data['email'] = 'invalid-email-format'
        
        response = self.client.post(reverse('signup'), invalid_email_data)
        self.assertEqual(response.status_code, 200)  # Form hataları ile geri döner
        self.assertFalse(User.objects.filter(username='integration_test_user').exists())
        
        # Şifre uyumsuzluğu
        password_mismatch_data = self.valid_data.copy()
        password_mismatch_data['password1'] = 'password123!'
        password_mismatch_data['password2'] = 'differentpassword123!'
        
        response = self.client.post(reverse('signup'), password_mismatch_data)
        self.assertEqual(response.status_code, 200)  # Form hataları ile geri döner
        self.assertFalse(User.objects.filter(username='integration_test_user').exists())


if __name__ == "__main__":
    print("Signup View Testleri Başlatılıyor...")
    print("=" * 60)
    
    # Test çalıştırma
    import unittest
    unittest.main()
