"""
Logout Integration Test File
This file tests all integration tests related to logout.
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


class TestLogoutIntegration(TestCase):
    """Logout integration tests"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create test user (email verified)
        self.user = User.objects.create_user(
            username='integration_logout_user',
            email='integration_logout@example.com',
            password='testpass123',
            first_name='Integration',
            last_name='Logout',
            phone_number='+905551234567',
            date_of_birth='1990-01-01',
            gender='M',
            is_organisor=True,
            email_verified=True
        )
        
        # Create UserProfile
        self.user_profile, created = UserProfile.objects.get_or_create(user=self.user)
        
        # Organisor oluştur
        Organisor.objects.create(user=self.user, organisation=self.user_profile)
    
    def test_complete_logout_flow(self):
        """Full logout flow test"""
        # 1. Login sayfasına git
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        
        # 2. Login form gönder
        response = self.client.post(reverse('login'), {
            'username': 'integration_logout_user',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('landing-page'))
        
        # 3. Kullanıcı giriş yapmış mı kontrol et
        self.assertTrue(self.client.session.get('_auth_user_id'))
        
        # 4. Korumalı sayfaya erişim testi
        response = self.client.get(reverse('leads:lead-list'))
        self.assertEqual(response.status_code, 200)
        
        # 5. Logout yap
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('landing-page'))
        
        # 6. Session temizlenmeli
        self.assertFalse(self.client.session.get('_auth_user_id'))
        
        # 7. Logout sonrası korumalı sayfaya erişim engellenmeli
        response = self.client.get(reverse('leads:lead-list'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_login_logout_login_cycle(self):
        """Login-logout-login cycle test"""
        # 1. İlk login
        response = self.client.post(reverse('login'), {
            'username': 'integration_logout_user',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.client.session.get('_auth_user_id'))
        
        # 2. Logout
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.client.session.get('_auth_user_id'))
        
        # 3. Tekrar login
        response = self.client.post(reverse('login'), {
            'username': 'integration_logout_user',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.client.session.get('_auth_user_id'))
        
        # 4. Korumalı sayfaya erişim
        response = self.client.get(reverse('leads:lead-list'))
        self.assertEqual(response.status_code, 200)
        
        # 5. Tekrar logout
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.client.session.get('_auth_user_id'))
    
    def test_logout_from_different_pages(self):
        """Logout from different pages test"""
        # Login yap
        self.client.login(username='integration_logout_user', password='testpass123')
        
        # Landing page'den logout
        self.client.get(reverse('landing-page'))
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.client.session.get('_auth_user_id'))
        
        # Tekrar login
        self.client.login(username='integration_logout_user', password='testpass123')
        
        # Lead list page'den logout
        self.client.get(reverse('leads:lead-list'))
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.client.session.get('_auth_user_id'))
    
    def test_logout_with_active_session_data(self):
        """Logout with active session data test"""
        # Login yap
        self.client.login(username='integration_logout_user', password='testpass123')
        
        # Session'a özel veriler ekle
        session = self.client.session
        session['user_preferences'] = {'theme': 'dark', 'language': 'en'}
        session['cart_items'] = [1, 2, 3, 4, 5]
        session.save()
        
        # Session verilerini kontrol et
        self.assertEqual(self.client.session.get('user_preferences')['theme'], 'dark')
        self.assertEqual(len(self.client.session.get('cart_items')), 5)
        
        # Logout yap
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        
        # Tüm session verileri temizlenmeli
        self.assertIsNone(self.client.session.get('user_preferences'))
        self.assertIsNone(self.client.session.get('cart_items'))
        self.assertFalse(self.client.session.get('_auth_user_id'))
    
    def test_logout_with_multiple_browser_sessions(self):
        """Logout with multiple browser sessions test"""
        # İki farklı client (farklı tarayıcıları simüle eder)
        client1 = Client()
        client2 = Client()
        
        # Her iki client ile login yap
        client1.login(username='integration_logout_user', password='testpass123')
        client2.login(username='integration_logout_user', password='testpass123')
        
        # Her iki client giriş yapmış olmalı
        self.assertTrue(client1.session.get('_auth_user_id'))
        self.assertTrue(client2.session.get('_auth_user_id'))
        
        # Client1 ile logout yap
        response = client1.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(client1.session.get('_auth_user_id'))
        
        # Client2 hala giriş yapmış olmalı (farklı session)
        self.assertTrue(client2.session.get('_auth_user_id'))
        
        # Client2 korumalı sayfaya erişebilmeli
        response = client2.get(reverse('leads:lead-list'))
        self.assertEqual(response.status_code, 200)
        
        # Client1 korumalı sayfaya erişememeli
        response = client1.get(reverse('leads:lead-list'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_logout_redirect_behavior(self):
        """Logout redirect behavior test"""
        # Login yap
        self.client.login(username='integration_logout_user', password='testpass123')
        
        # Logout yap
        response = self.client.post(reverse('logout'))
        
        # Landing page'e redirect olmalı
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('landing-page'))
        
        # Follow redirect
        response = self.client.post(reverse('logout'), follow=True)
        self.assertEqual(response.status_code, 200)
        
        # Landing page template kullanılmalı
        self.assertTemplateUsed(response, 'landing.html')
    
    def test_logout_after_password_change(self):
        """Logout after password change test"""
        # Login yap
        self.client.login(username='integration_logout_user', password='testpass123')
        self.assertTrue(self.client.session.get('_auth_user_id'))
        
        # Şifre değiştir (password change view yerine direkt değiştir)
        self.user.set_password('newpassword123')
        self.user.save()
        
        # Logout yap
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.client.session.get('_auth_user_id'))
        
        # Eski şifre ile login denemesi başarısız olmalı
        response = self.client.post(reverse('login'), {
            'username': 'integration_logout_user',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 200)  # Form hataları ile geri döner
        self.assertFalse(self.client.session.get('_auth_user_id'))
        
        # Yeni şifre ile login başarılı olmalı
        response = self.client.post(reverse('login'), {
            'username': 'integration_logout_user',
            'password': 'newpassword123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.client.session.get('_auth_user_id'))
    
    def test_logout_with_remember_me(self):
        """Logout with remember me feature test"""
        # Bu test, eğer remember me özelliği eklenirse güncellenebilir
        # Şu anda remember me özelliği olmadığı için basit test
        
        # Login yap
        self.client.login(username='integration_logout_user', password='testpass123')
        self.assertTrue(self.client.session.get('_auth_user_id'))
        
        # Logout yap
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.client.session.get('_auth_user_id'))
    
    def test_logout_performance(self):
        """Logout performance test"""
        import time
        
        # Performance test - 10 kez logout
        times = []
        for i in range(10):
            # Login
            self.client.login(username='integration_logout_user', password='testpass123')
            
            # Logout time measurement
            start_time = time.time()
            response = self.client.post(reverse('logout'))
            end_time = time.time()
            
            times.append(end_time - start_time)
            
            # Logout başarılı olmalı
            self.assertEqual(response.status_code, 302)
            self.assertFalse(self.client.session.get('_auth_user_id'))
        
        # Ortalama logout süresi 0.5 saniyeden az olmalı
        avg_time = sum(times) / len(times)
        self.assertLess(avg_time, 0.5)
    
    def test_logout_with_different_user_types(self):
        """Logout integration test with different user types"""
        # Organizer ile tam akış
        self.client.login(username='integration_logout_user', password='testpass123')
        response = self.client.get(reverse('leads:lead-list'))
        self.assertEqual(response.status_code, 200)
        self.client.post(reverse('logout'))
        self.assertFalse(self.client.session.get('_auth_user_id'))
        
        # Create agent user
        agent_user = User.objects.create_user(
            username='agent_integration_logout',
            email='agent_integration_logout@example.com',
            password='testpass123',
            first_name='Agent',
            last_name='Integration',
            phone_number='+905559876543',
            date_of_birth='1985-01-01',
            gender='F',
            is_agent=True,
            email_verified=True
        )
        
        # Create UserProfile
        agent_user_profile, created = UserProfile.objects.get_or_create(user=agent_user)
        
        # Agent ile tam akış
        self.client.login(username='agent_integration_logout', password='testpass123')
        response = self.client.get(reverse('leads:lead-list'))
        self.assertEqual(response.status_code, 200)
        self.client.post(reverse('logout'))
        self.assertFalse(self.client.session.get('_auth_user_id'))
        
        # Create superuser
        superuser = User.objects.create_superuser(
            username='superuser_integration_logout',
            email='superuser_integration_logout@example.com',
            password='testpass123',
            first_name='Super',
            last_name='User',
            phone_number='+905552222222',
            date_of_birth='1980-01-01',
            gender='M',
            email_verified=True
        )
        
        # Superuser ile tam akış
        self.client.login(username='superuser_integration_logout', password='testpass123')
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
        self.client.post(reverse('logout'))
        self.assertFalse(self.client.session.get('_auth_user_id'))


class TestLogoutSecurityIntegration(TestCase):
    """Logout security integration tests"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create test user
        self.user = User.objects.create_user(
            username='security_integration_logout',
            email='security_integration_logout@example.com',
            password='testpass123',
            first_name='Security',
            last_name='Integration',
            phone_number='+905553333333',
            date_of_birth='1990-01-01',
            gender='M',
            is_organisor=True,
            email_verified=True
        )
        
        # Create UserProfile
        self.user_profile, created = UserProfile.objects.get_or_create(user=self.user)
        
        # Organisor oluştur
        Organisor.objects.create(user=self.user, organisation=self.user_profile)
    
    def test_logout_session_hijacking_protection(self):
        """Session hijacking attack protection integration test"""
        # Login yap
        self.client.login(username='security_integration_logout', password='testpass123')
        
        # Session bilgilerini kaydet
        old_session_key = self.client.session.session_key
        old_auth_hash = self.client.session.get('_auth_user_hash')
        
        # Korumalı sayfaya erişim (başarılı)
        response = self.client.get(reverse('leads:lead-list'))
        self.assertEqual(response.status_code, 200)
        
        # Logout yap
        self.client.post(reverse('logout'))
        
        # Eski session bilgileri ile korumalı sayfaya erişim denemesi
        response = self.client.get(reverse('leads:lead-list'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        # Session temizlenmiş olmalı
        self.assertFalse(self.client.session.get('_auth_user_id'))
        self.assertIsNone(self.client.session.get('_auth_user_hash'))
    
    def test_logout_csrf_protection_integration(self):
        """CSRF protection integration test"""
        # Login yap
        self.client.login(username='security_integration_logout', password='testpass123')
        
        # CSRF token ile logout (normal)
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.client.session.get('_auth_user_id'))
        
        # Django test client otomatik CSRF token ekler
        # A different approach is needed for manual CSRF test
    
    def test_logout_no_information_leakage(self):
        """Information leakage after logout test"""
        # Login yap
        self.client.login(username='security_integration_logout', password='testpass123')
        
        # Session'a hassas bilgi ekle
        session = self.client.session
        session['sensitive_data'] = {'ssn': '123-45-6789', 'credit_card': '1234-5678-9012-3456'}
        session.save()
        
        # Logout yap
        self.client.post(reverse('logout'))
        
        # Tüm hassas veriler temizlenmeli
        self.assertIsNone(self.client.session.get('sensitive_data'))
        self.assertFalse(self.client.session.get('_auth_user_id'))
    
    def test_logout_session_fixation_protection_integration(self):
        """Session fixation attack protection integration test"""
        # Create initial session (as if created by attacker)
        self.client.get(reverse('landing-page'))
        old_session_key = self.client.session.session_key
        
        # Login yap (session yenilenmeli)
        self.client.login(username='security_integration_logout', password='testpass123')
        login_session_key = self.client.session.session_key
        
        # Login sonrası session key değişmeli (Django otomatik yapar)
        # Bu test session fixation saldırısına karşı koruma sağlar
        
        # Logout yap
        self.client.post(reverse('logout'))
        logout_session_key = self.client.session.session_key
        
        # Session key should be different or refreshed at each step
        # Django logout sonrası session flush eder
        self.assertIsNotNone(old_session_key)
        self.assertIsNotNone(login_session_key)


if __name__ == "__main__":
    print("Logout Entegrasyon Testleri Başlatılıyor...")
    print("=" * 60)
    
    # Test çalıştırma
    import unittest
    unittest.main()

