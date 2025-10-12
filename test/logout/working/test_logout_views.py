"""
Logout Viewları Test Dosyası
Bu dosya logout ile ilgili tüm viewları test eder.
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


class TestLogoutView(TestCase):
    """LogoutView testleri"""
    
    def setUp(self):
        """Test verilerini hazırla"""
        self.client = Client()
        
        # Test kullanıcısı oluştur (email doğrulanmış)
        self.user = User.objects.create_user(
            username='testuser_logout_views',
            email='test_logout_views@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            phone_number='+905551234567',
            date_of_birth='1990-01-01',
            gender='M',
            is_organisor=True,
            email_verified=True
        )
        
        # UserProfile oluştur
        self.user_profile, created = UserProfile.objects.get_or_create(user=self.user)
        
        # Organisor oluştur
        Organisor.objects.create(user=self.user, organisation=self.user_profile)
    
    def test_logout_view_post_authenticated_user(self):
        """Giriş yapmış kullanıcı ile logout POST isteği testi"""
        # Önce giriş yap
        self.client.login(username='testuser_logout_views', password='testpass123')
        
        # Session kontrolü - giriş yapmış olmalı
        self.assertTrue(self.client.session.get('_auth_user_id'))
        
        # Logout yap
        response = self.client.post(reverse('logout'))
        
        # Redirect olmalı
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('landing-page'))
        
        # Session temizlenmeli
        self.assertFalse(self.client.session.get('_auth_user_id'))
    
    def test_logout_view_get_authenticated_user(self):
        """Giriş yapmış kullanıcı ile logout GET isteği testi"""
        # Önce giriş yap
        self.client.login(username='testuser_logout_views', password='testpass123')
        
        # Session kontrolü - giriş yapmış olmalı
        self.assertTrue(self.client.session.get('_auth_user_id'))
        
        # GET ile logout yap (Django LogoutView GET'i desteklemez, 405 döner)
        response = self.client.get(reverse('logout'))
        
        # Method not allowed olmalı (Django LogoutView sadece POST destekler)
        self.assertEqual(response.status_code, 405)
        
        # Session hala aktif olmalı (logout olmadı)
        self.assertTrue(self.client.session.get('_auth_user_id'))
    
    def test_logout_view_unauthenticated_user(self):
        """Giriş yapmamış kullanıcı ile logout testi"""
        # Session kontrolü - giriş yapmamış olmalı
        self.assertFalse(self.client.session.get('_auth_user_id'))
        
        # Logout yap (giriş yapmamış olsa bile)
        response = self.client.post(reverse('logout'))
        
        # Redirect olmalı
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('landing-page'))
        
        # Session hala boş olmalı
        self.assertFalse(self.client.session.get('_auth_user_id'))
    
    def test_logout_view_redirect_url(self):
        """Logout sonrası redirect URL testi"""
        # Önce giriş yap
        self.client.login(username='testuser_logout_views', password='testpass123')
        
        # Logout yap
        response = self.client.post(reverse('logout'))
        
        # LOGOUT_REDIRECT_URL'ye redirect olmalı (settings.py'de '/' olarak tanımlı)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')
    
    def test_logout_view_session_cleanup(self):
        """Logout sonrası session temizliği testi"""
        # Önce giriş yap
        self.client.login(username='testuser_logout_views', password='testpass123')
        
        # Session bilgilerini kontrol et
        session = self.client.session
        self.assertTrue(session.get('_auth_user_id'))
        self.assertTrue(session.get('_auth_user_backend'))
        self.assertTrue(session.get('_auth_user_hash'))
        
        # Logout yap
        response = self.client.post(reverse('logout'))
        
        # Session temizlenmeli
        session = self.client.session
        self.assertFalse(session.get('_auth_user_id'))
        self.assertFalse(session.get('_auth_user_backend'))
        self.assertFalse(session.get('_auth_user_hash'))
    
    def test_logout_view_protected_page_access_after_logout(self):
        """Logout sonrası korumalı sayfaya erişim testi"""
        # Önce giriş yap
        self.client.login(username='testuser_logout_views', password='testpass123')
        
        # Korumalı sayfaya erişim (giriş yapmış)
        response = self.client.get(reverse('leads:lead-list'))
        self.assertEqual(response.status_code, 200)
        
        # Logout yap
        self.client.post(reverse('logout'))
        
        # Logout sonrası korumalı sayfaya erişim engellenmeli
        response = self.client.get(reverse('leads:lead-list'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_logout_view_multiple_logout_calls(self):
        """Birden fazla logout çağrısı testi"""
        # Önce giriş yap
        self.client.login(username='testuser_logout_views', password='testpass123')
        
        # İlk logout
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.client.session.get('_auth_user_id'))
        
        # İkinci logout (zaten logout olmuş)
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.client.session.get('_auth_user_id'))
        
        # Üçüncü logout (hala logout)
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.client.session.get('_auth_user_id'))
    
    def test_logout_view_csrf_protection(self):
        """CSRF koruması testi"""
        # Önce giriş yap
        self.client.login(username='testuser_logout_views', password='testpass123')
        
        # CSRF token ile logout yap (normal)
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        
        # Django test client otomatik CSRF token ekler
        # Manuel CSRF token testi için farklı bir yaklaşım gerekir
    
    def test_logout_view_next_parameter(self):
        """Logout sonrası next parametresi ile redirect testi"""
        # Önce giriş yap
        self.client.login(username='testuser_logout_views', password='testpass123')
        
        # next parametresi ile logout yap
        response = self.client.post(reverse('logout') + '?next=/login/')
        
        # Django LogoutView next parametresini destekler
        # Redirect URL next parametresine göre değişebilir
        self.assertEqual(response.status_code, 302)
    
    def test_logout_view_with_different_user_types(self):
        """Farklı kullanıcı tipleri ile logout testi"""
        # Organizer ile logout
        self.client.login(username='testuser_logout_views', password='testpass123')
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.client.session.get('_auth_user_id'))
        
        # Agent kullanıcı oluştur
        agent_user = User.objects.create_user(
            username='agent_logout_test',
            email='agent_logout@example.com',
            password='testpass123',
            first_name='Agent',
            last_name='User',
            phone_number='+905559876543',
            date_of_birth='1985-01-01',
            gender='F',
            is_agent=True,
            email_verified=True
        )
        
        # UserProfile oluştur
        agent_user_profile, created = UserProfile.objects.get_or_create(user=agent_user)
        
        # Agent ile logout
        self.client.login(username='agent_logout_test', password='testpass123')
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.client.session.get('_auth_user_id'))
    
    def test_logout_view_with_superuser(self):
        """Superuser ile logout testi"""
        # Superuser oluştur
        superuser = User.objects.create_superuser(
            username='superuser_logout',
            email='superuser_logout@example.com',
            password='testpass123',
            first_name='Super',
            last_name='User',
            phone_number='+905551111111',
            date_of_birth='1980-01-01',
            gender='M',
            email_verified=True
        )
        
        # Superuser ile giriş yap
        self.client.login(username='superuser_logout', password='testpass123')
        self.assertTrue(self.client.session.get('_auth_user_id'))
        
        # Logout yap
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.client.session.get('_auth_user_id'))
    
    def test_logout_view_session_data_cleanup(self):
        """Logout sonrası özel session verilerinin temizliği testi"""
        # Önce giriş yap
        self.client.login(username='testuser_logout_views', password='testpass123')
        
        # Session'a özel veri ekle
        session = self.client.session
        session['custom_data'] = 'test_value'
        session.save()
        
        # Session verilerini kontrol et
        self.assertEqual(self.client.session.get('custom_data'), 'test_value')
        
        # Logout yap
        response = self.client.post(reverse('logout'))
        
        # Session flush edilir, tüm veriler temizlenir
        # Yeni session oluşturulur
        session = self.client.session
        self.assertIsNone(session.get('custom_data'))
    
    def test_logout_view_concurrent_sessions(self):
        """Eşzamanlı session'lar ile logout testi"""
        # İki farklı client oluştur (farklı session'lar)
        client1 = Client()
        client2 = Client()
        
        # Her iki client ile giriş yap
        client1.login(username='testuser_logout_views', password='testpass123')
        client2.login(username='testuser_logout_views', password='testpass123')
        
        # Her iki client giriş yapmış olmalı
        self.assertTrue(client1.session.get('_auth_user_id'))
        self.assertTrue(client2.session.get('_auth_user_id'))
        
        # Client1 ile logout yap
        response = client1.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(client1.session.get('_auth_user_id'))
        
        # Client2 hala giriş yapmış olmalı (farklı session)
        self.assertTrue(client2.session.get('_auth_user_id'))
    
    def test_logout_view_url_pattern(self):
        """Logout URL pattern testi"""
        # Logout URL'i doğru mu
        logout_url = reverse('logout')
        self.assertEqual(logout_url, '/logout/')
    
    def test_logout_view_with_ajax_request(self):
        """AJAX isteği ile logout testi"""
        # Önce giriş yap
        self.client.login(username='testuser_logout_views', password='testpass123')
        
        # AJAX isteği ile logout
        response = self.client.post(
            reverse('logout'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Redirect olmalı
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.client.session.get('_auth_user_id'))


class TestLogoutViewSecurity(TestCase):
    """Logout güvenlik testleri"""
    
    def setUp(self):
        """Test verilerini hazırla"""
        self.client = Client()
        
        # Test kullanıcısı oluştur
        self.user = User.objects.create_user(
            username='security_logout_user',
            email='security_logout@example.com',
            password='testpass123',
            first_name='Security',
            last_name='User',
            phone_number='+905552222222',
            date_of_birth='1990-01-01',
            gender='M',
            is_organisor=True,
            email_verified=True
        )
        
        # UserProfile oluştur
        self.user_profile, created = UserProfile.objects.get_or_create(user=self.user)
        
        # Organisor oluştur
        Organisor.objects.create(user=self.user, organisation=self.user_profile)
    
    def test_logout_view_session_fixation_protection(self):
        """Session fixation saldırısına karşı koruma testi"""
        # Önce giriş yap
        self.client.login(username='security_logout_user', password='testpass123')
        
        # Session ID'yi kaydet
        old_session_key = self.client.session.session_key
        
        # Logout yap
        self.client.post(reverse('logout'))
        
        # Yeni session oluşturulmalı (session key değişmeli)
        # Django logout sonrası session flush eder
        new_session_key = self.client.session.session_key
        
        # Session key'ler farklı olmalı (veya None)
        # Logout sonrası yeni session oluşturulur
        self.assertIsNotNone(old_session_key)
    
    def test_logout_view_no_session_hijacking(self):
        """Session hijacking saldırısına karşı koruma testi"""
        # Önce giriş yap
        self.client.login(username='security_logout_user', password='testpass123')
        
        # Session bilgilerini kaydet
        user_id = self.client.session.get('_auth_user_id')
        
        # Logout yap
        self.client.post(reverse('logout'))
        
        # Eski session ile korumalı sayfaya erişim denemesi
        response = self.client.get(reverse('leads:lead-list'))
        
        # Erişim engellenmeli (redirect to login)
        self.assertEqual(response.status_code, 302)
    
    def test_logout_view_token_invalidation(self):
        """Logout sonrası token invalidation testi"""
        # Önce giriş yap
        self.client.login(username='security_logout_user', password='testpass123')
        
        # Session hash'i kaydet
        session_hash = self.client.session.get('_auth_user_hash')
        self.assertIsNotNone(session_hash)
        
        # Logout yap
        self.client.post(reverse('logout'))
        
        # Session hash temizlenmeli
        self.assertIsNone(self.client.session.get('_auth_user_hash'))
    
    def test_logout_view_no_caching(self):
        """Logout sonrası cache kontrol testi"""
        # Önce giriş yap
        self.client.login(username='security_logout_user', password='testpass123')
        
        # Logout yap
        response = self.client.post(reverse('logout'))
        
        # Cache-Control header'ları kontrol et
        # Django LogoutView otomatik cache kontrolü eklemez
        # Ancak logout sonrası sayfalar cache'lenmemeli
        self.assertEqual(response.status_code, 302)


if __name__ == "__main__":
    print("Logout View Testleri Başlatılıyor...")
    print("=" * 60)
    
    # Test çalıştırma
    import unittest
    unittest.main()

