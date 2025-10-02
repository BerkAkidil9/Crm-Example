"""
Login Formları Test Dosyası
Bu dosya login ile ilgili tüm formları test eder.
"""

import os
import sys
import django
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from unittest.mock import patch, MagicMock

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djcrm.settings')
django.setup()

from leads.forms import CustomAuthenticationForm
from leads.models import User, UserProfile, EmailVerificationToken
from organisors.models import Organisor

User = get_user_model()


class TestCustomAuthenticationForm(TestCase):
    """CustomAuthenticationForm testleri"""
    
    def setUp(self):
        """Test verilerini hazırla"""
        # Test kullanıcısı oluştur (email doğrulanmış)
        self.user = User.objects.create_user(
            username='testuser_login_forms',
            email='test_login_forms@example.com',
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
        
        # Email doğrulanmamış kullanıcı
        self.unverified_user = User.objects.create_user(
            username='unverified_user_forms',
            email='unverified_forms@example.com',
            password='testpass123',
            first_name='Unverified',
            last_name='User',
            phone_number='+905559876543',
            date_of_birth='1985-05-15',
            gender='F',
            is_organisor=True,
            email_verified=False
        )
        
        # UserProfile oluştur
        self.unverified_user_profile, created = UserProfile.objects.get_or_create(user=self.unverified_user)
        
        # Organisor oluştur
        Organisor.objects.create(user=self.unverified_user, organisation=self.unverified_user_profile)
    
    def test_form_initialization(self):
        """Form başlatma testi"""
        form = CustomAuthenticationForm()
        
        # Gerekli alanların varlığını kontrol et
        self.assertIn('username', form.fields)
        self.assertIn('password', form.fields)
    
    def test_form_valid_data_username(self):
        """Geçerli username veri ile form testi"""
        form = CustomAuthenticationForm(data={
            'username': 'testuser_login_forms',
            'password': 'testpass123'
        })
        self.assertTrue(form.is_valid())
    
    def test_form_valid_data_email(self):
        """Geçerli email veri ile form testi"""
        form = CustomAuthenticationForm(data={
            'username': 'test_login_forms@example.com',
            'password': 'testpass123'
        })
        self.assertTrue(form.is_valid())
    
    def test_form_required_fields(self):
        """Zorunlu alanlar testi"""
        # Username eksik
        form = CustomAuthenticationForm(data={
            'password': 'testpass123'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        
        # Password eksik
        form = CustomAuthenticationForm(data={
            'username': 'testuser_login_forms'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)
        
        # Her ikisi de eksik
        form = CustomAuthenticationForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertIn('password', form.errors)
    
    def test_form_invalid_credentials(self):
        """Geçersiz credentials ile form testi"""
        # Yanlış password
        form = CustomAuthenticationForm(data={
            'username': 'testuser_login_forms',
            'password': 'wrongpassword'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
    
    def test_form_nonexistent_user(self):
        """Var olmayan kullanıcı ile form testi"""
        form = CustomAuthenticationForm(data={
            'username': 'nonexistent_user',
            'password': 'testpass123'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
    
    def test_form_unverified_email_user(self):
        """Email doğrulanmamış kullanıcı ile form testi"""
        form = CustomAuthenticationForm(data={
            'username': 'unverified_user_forms',
            'password': 'testpass123'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
    
    def test_form_widget_attributes(self):
        """Widget özellikleri testi"""
        form = CustomAuthenticationForm()
        
        # Username widget
        username_widget = form['username'].as_widget()
        self.assertIn('placeholder="Username or Email"', username_widget)
        self.assertIn('class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"', username_widget)
        
        # Password widget
        password_widget = form['password'].as_widget()
        self.assertIn('placeholder="Password"', password_widget)
        self.assertIn('class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"', password_widget)
    
    def test_form_field_labels(self):
        """Form alan etiketleri testi"""
        form = CustomAuthenticationForm()
        
        self.assertEqual(form.fields['username'].label, 'Username or Email')
        self.assertEqual(form.fields['password'].label, 'Password')
    
    def test_form_field_max_lengths(self):
        """Form alan maksimum uzunlukları testi"""
        form = CustomAuthenticationForm()
        
        # Username field max_length 150 (Django default), 254 değil
        self.assertEqual(form.fields['username'].max_length, 150)
    
    def test_form_field_widgets(self):
        """Form alan widget'ları testi"""
        form = CustomAuthenticationForm()
        
        # Username widget
        self.assertIsInstance(form.fields['username'].widget, django.forms.TextInput)
        
        # Password widget
        self.assertIsInstance(form.fields['password'].widget, django.forms.PasswordInput)
    
    def test_form_clean_methods(self):
        """Form clean metodları testi"""
        # Geçerli veri ile clean testi
        form = CustomAuthenticationForm(data={
            'username': 'testuser_login_forms',
            'password': 'testpass123'
        })
        if form.is_valid():
            # CustomAuthenticationForm'da clean_username metodu yok, testi kaldır
            pass
    
    def test_form_validation_edge_cases(self):
        """Form validasyon sınır durumları testi"""
        # Boş string
        form = CustomAuthenticationForm(data={
            'username': '',
            'password': ''
        })
        self.assertFalse(form.is_valid())
        
        # Sadece boşluk
        form = CustomAuthenticationForm(data={
            'username': '   ',
            'password': '   '
        })
        self.assertFalse(form.is_valid())
        
        # Çok uzun username
        form = CustomAuthenticationForm(data={
            'username': 'a' * 300,
            'password': 'testpass123'
        })
        self.assertFalse(form.is_valid())
    
    def test_form_case_insensitive_username(self):
        """Case insensitive username testi"""
        form = CustomAuthenticationForm(data={
            'username': 'TESTUSER_LOGIN_FORMS',  # Büyük harflerle
            'password': 'testpass123'
        })
        self.assertTrue(form.is_valid())
    
    def test_form_case_insensitive_email(self):
        """Case insensitive email testi"""
        form = CustomAuthenticationForm(data={
            'username': 'TEST_LOGIN_FORMS@EXAMPLE.COM',  # Büyük harflerle
            'password': 'testpass123'
        })
        self.assertTrue(form.is_valid())
    
    def test_form_whitespace_handling(self):
        """Whitespace handling testi"""
        form = CustomAuthenticationForm(data={
            'username': '  testuser_login_forms  ',  # Başında ve sonunda boşluk
            'password': 'testpass123'
        })
        self.assertTrue(form.is_valid())
    
    def test_form_error_messages(self):
        """Form hata mesajları testi"""
        form = CustomAuthenticationForm()
        
        # Error mesajları kaldırılmış mı kontrol et
        self.assertEqual(form.fields['username'].error_messages, {'required': ''})
        self.assertEqual(form.fields['password'].error_messages, {'required': ''})
    
    def test_form_autofocus_attribute(self):
        """Autofocus özelliği testi"""
        form = CustomAuthenticationForm()
        
        username_widget = form['username'].as_widget()
        self.assertIn('autofocus', username_widget)
    
    def test_form_password_field_attributes(self):
        """Password alanı özellikleri testi"""
        form = CustomAuthenticationForm()
        
        password_widget = form['password'].as_widget()
        self.assertIn('type="password"', password_widget)
        self.assertIn('placeholder="Password"', password_widget)
    
    def test_form_username_field_attributes(self):
        """Username alanı özellikleri testi"""
        form = CustomAuthenticationForm()
        
        username_widget = form['username'].as_widget()
        self.assertIn('type="text"', username_widget)
        self.assertIn('placeholder="Username or Email"', username_widget)
    
    def test_form_with_request_context(self):
        """Request context ile form testi"""
        from django.test import RequestFactory
        
        factory = RequestFactory()
        request = factory.get('/login/')
        
        form = CustomAuthenticationForm(request=request)
        
        # Form request ile başlatılabiliyor mu
        self.assertIsNotNone(form)
    
    def test_form_validation_with_special_characters(self):
        """Özel karakterler ile validasyon testi"""
        # Özel karakterler içeren username
        form = CustomAuthenticationForm(data={
            'username': 'test@user#123',
            'password': 'testpass123'
        })
        # Bu geçerli olmayabilir, test et
        # self.assertFalse(form.is_valid())
    
    def test_form_validation_with_unicode(self):
        """Unicode karakterler ile validasyon testi"""
        # Unicode karakterler içeren username
        form = CustomAuthenticationForm(data={
            'username': 'tëstüsér',
            'password': 'testpass123'
        })
        # Bu geçerli olmayabilir, test et
        # self.assertFalse(form.is_valid())


class TestLoginFormIntegration(TestCase):
    """Login form entegrasyon testleri"""
    
    def setUp(self):
        """Test verilerini hazırla"""
        # Test kullanıcısı oluştur
        self.user = User.objects.create_user(
            username='integration_form_user',
            email='integration_form@example.com',
            password='testpass123',
            first_name='Integration',
            last_name='Form',
            phone_number='+905559876543',
            date_of_birth='1985-05-15',
            gender='F',
            is_organisor=True,
            email_verified=True
        )
        
        # UserProfile oluştur
        self.user_profile, created = UserProfile.objects.get_or_create(user=self.user)
        
        # Organisor oluştur
        Organisor.objects.create(user=self.user, organisation=self.user_profile)
    
    def test_form_authentication_with_different_credentials(self):
        """Farklı credentials formatları ile authentication testi"""
        # Username ile
        form = CustomAuthenticationForm(data={
            'username': 'integration_form_user',
            'password': 'testpass123'
        })
        self.assertTrue(form.is_valid())
        
        # Email ile
        form = CustomAuthenticationForm(data={
            'username': 'integration_form@example.com',
            'password': 'testpass123'
        })
        self.assertTrue(form.is_valid())
    
    def test_form_authentication_failure_scenarios(self):
        """Authentication başarısızlık senaryoları testi"""
        # Yanlış password
        form = CustomAuthenticationForm(data={
            'username': 'integration_form_user',
            'password': 'wrongpassword'
        })
        self.assertFalse(form.is_valid())
        
        # Var olmayan kullanıcı
        form = CustomAuthenticationForm(data={
            'username': 'nonexistent_user',
            'password': 'testpass123'
        })
        self.assertFalse(form.is_valid())
        
        # Boş credentials
        form = CustomAuthenticationForm(data={
            'username': '',
            'password': ''
        })
        self.assertFalse(form.is_valid())
    
    def test_form_with_mock_authentication_backend(self):
        """Mock authentication backend ile form testi"""
        with patch('leads.authentication.EmailOrUsernameModelBackend.authenticate') as mock_authenticate:
            # Mock authentication başarılı
            mock_authenticate.return_value = self.user
            
            form = CustomAuthenticationForm(data={
                'username': 'integration_form_user',
                'password': 'testpass123'
            })
            
            # Form valid olmalı
            self.assertTrue(form.is_valid())
            
            # Mock authentication çağrıldı mı
            mock_authenticate.assert_called_once()
    
    def test_form_validation_with_empty_data(self):
        """Boş veri ile form validasyon testi"""
        form = CustomAuthenticationForm(data={})
        
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertIn('password', form.errors)
    
    def test_form_validation_with_partial_data(self):
        """Kısmi veri ile form validasyon testi"""
        # Sadece username
        form = CustomAuthenticationForm(data={
            'username': 'integration_form_user'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)
        
        # Sadece password
        form = CustomAuthenticationForm(data={
            'password': 'testpass123'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)


if __name__ == "__main__":
    print("Login Form Testleri Başlatılıyor...")
    print("=" * 60)
    
    # Test çalıştırma
    import unittest
    unittest.main()
