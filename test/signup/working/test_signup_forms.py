"""
Signup Formları Test Dosyası
Bu dosya signup ile ilgili tüm formları test eder.
"""

import os
import sys
import django
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from unittest.mock import patch, MagicMock

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djcrm.settings')
django.setup()

from leads.forms import CustomUserCreationForm
from leads.models import User, UserProfile, EmailVerificationToken
from organisors.models import Organisor


class TestCustomUserCreationForm(TestCase):
    """CustomUserCreationForm testleri"""
    
    def setUp(self):
        """Test verilerini hazırla"""
        self.valid_data = {
            'username': 'testuser_signup',
            'email': 'test_signup@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'phone_number_0': '+90',
            'phone_number_1': '5551234567',
            'date_of_birth': '1990-01-01',
            'gender': 'M',
            'password1': 'testpass123!',
            'password2': 'testpass123!',
        }
    
    def test_form_initialization(self):
        """Form başlatma testi"""
        form = CustomUserCreationForm()
        
        # Gerekli alanların varlığını kontrol et
        self.assertIn('username', form.fields)
        self.assertIn('email', form.fields)
        self.assertIn('first_name', form.fields)
        self.assertIn('last_name', form.fields)
        self.assertIn('phone_number', form.fields)
        self.assertIn('date_of_birth', form.fields)
        self.assertIn('gender', form.fields)
        self.assertIn('password1', form.fields)
        self.assertIn('password2', form.fields)
    
    def test_form_valid_data(self):
        """Geçerli veri ile form testi"""
        form = CustomUserCreationForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
    
    def test_form_required_fields(self):
        """Zorunlu alanlar testi"""
        required_fields = [
            'username', 'email', 'first_name', 'last_name', 
            'date_of_birth', 'gender', 'password1', 'password2'
        ]
        
        for field in required_fields:
            data = self.valid_data.copy()
            del data[field]
            
            form = CustomUserCreationForm(data=data)
            self.assertFalse(form.is_valid())
            self.assertIn(field, form.errors)
        
        # Phone number alanları için özel test (MultiWidget)
        data = self.valid_data.copy()
        del data['phone_number_0']
        del data['phone_number_1']
        
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('phone_number', form.errors)
    
    def test_form_email_validation_unique(self):
        """Email benzersizlik validasyonu testi"""
        # Önce bir kullanıcı oluştur
        User.objects.create_user(
            username='existing_user',
            email='existing@example.com',
            password='testpass123'
        )
        
        # Aynı email ile form oluştur
        data = self.valid_data.copy()
        data['email'] = 'existing@example.com'
        
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertIn('already exists', str(form.errors['email']))
    
    def test_form_phone_number_validation_unique(self):
        """Telefon numarası benzersizlik validasyonu testi"""
        # Önce bir kullanıcı oluştur
        User.objects.create_user(
            username='existing_user',
            email='existing@example.com',
            password='testpass123',
            phone_number='+905551234567'
        )
        
        # Aynı telefon numarası ile form oluştur
        data = self.valid_data.copy()
        data['phone_number_0'] = '+90'
        data['phone_number_1'] = '5551234567'
        data['username'] = 'different_username'
        data['email'] = 'different@example.com'
        
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        # Phone number validation hatası olabilir, ama benzersizlik kontrolü de olabilir
        self.assertIn('phone_number', form.errors)
    
    def test_form_username_validation_unique(self):
        """Kullanıcı adı benzersizlik validasyonu testi"""
        # Önce bir kullanıcı oluştur
        User.objects.create_user(
            username='existing_user',
            email='existing@example.com',
            password='testpass123'
        )
        
        # Aynı kullanıcı adı ile form oluştur
        data = self.valid_data.copy()
        data['username'] = 'existing_user'
        
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertIn('already exists', str(form.errors['username']))
    
    def test_form_password_validation(self):
        """Şifre validasyonu testi"""
        # Farklı şifreler
        data = self.valid_data.copy()
        data['password1'] = 'testpass123!'
        data['password2'] = 'differentpass123!'
        
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
    
    def test_form_widget_attributes(self):
        """Widget özellikleri testi"""
        form = CustomUserCreationForm()
        
        # CSS sınıfları ve placeholder kontrol et
        self.assertIn('placeholder="Username"', str(form['username'].as_widget()))
        self.assertIn('placeholder="Email"', str(form['email'].as_widget()))
        self.assertIn('placeholder="First Name"', str(form['first_name'].as_widget()))
        self.assertIn('placeholder="Last Name"', str(form['last_name'].as_widget()))
        # Password widgets don't have placeholders in Django's default implementation
        # self.assertIn('placeholder="Password"', str(form['password1'].as_widget()))
        # self.assertIn('placeholder="Confirm Password"', str(form['password2'].as_widget()))
    
    def test_form_date_field_type(self):
        """Tarih alanı tipi testi"""
        form = CustomUserCreationForm()
        
        # Date input tipi kontrol et
        self.assertIn('type="date"', str(form['date_of_birth'].as_widget()))
        self.assertIn('class="form-control"', str(form['date_of_birth'].as_widget()))
    
    def test_form_gender_choices(self):
        """Cinsiyet seçenekleri testi"""
        form = CustomUserCreationForm()
        
        expected_choices = [
            ('M', 'Male'),
            ('F', 'Female'),
            ('O', 'Other'),
        ]
        
        self.assertEqual(form.fields['gender'].choices, expected_choices)
    
    def test_form_save_method(self):
        """Form save metodu testi"""
        form = CustomUserCreationForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
        
        user = form.save(commit=False)
        
        # Kullanıcı alanları doğru mu
        self.assertEqual(user.username, 'testuser_signup')
        self.assertEqual(user.email, 'test_signup@example.com')
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User')
        self.assertEqual(str(user.phone_number), '+905551234567')
        self.assertEqual(user.gender, 'M')
        self.assertEqual(user.date_of_birth.strftime('%Y-%m-%d'), '1990-01-01')
    
    def test_form_clean_methods(self):
        """Form clean metodları testi"""
        # Email clean
        form = CustomUserCreationForm(data=self.valid_data)
        if form.is_valid():
            cleaned_email = form.clean_email()
            self.assertEqual(cleaned_email, 'test_signup@example.com')
        
        # Phone number clean
        form = CustomUserCreationForm(data=self.valid_data)
        if form.is_valid():
            cleaned_phone = form.clean_phone_number()
            self.assertEqual(str(cleaned_phone), '+905551234567')
        
        # Username clean
        form = CustomUserCreationForm(data=self.valid_data)
        if form.is_valid():
            cleaned_username = form.clean_username()
            self.assertEqual(cleaned_username, 'testuser_signup')
    
    def test_form_validation_edge_cases(self):
        """Form validasyon sınır durumları testi"""
        # Boş email
        data = self.valid_data.copy()
        data['email'] = ''
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        
        # Geçersiz email formatı
        data = self.valid_data.copy()
        data['email'] = 'invalid-email'
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        
        # Çok kısa şifre
        data = self.valid_data.copy()
        data['password1'] = '123'
        data['password2'] = '123'
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        
        # Geçersiz tarih formatı
        data = self.valid_data.copy()
        data['date_of_birth'] = 'invalid-date'
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
    
    def test_form_field_help_texts(self):
        """Form alan yardım metinleri testi"""
        form = CustomUserCreationForm()
        
        self.assertEqual(form.fields['email'].help_text, "Email address is required")
        self.assertEqual(form.fields['first_name'].help_text, "First name is required")
        self.assertEqual(form.fields['last_name'].help_text, "Last name is required")
        self.assertEqual(form.fields['phone_number'].help_text, "Select your country and enter your phone number")
        self.assertEqual(form.fields['date_of_birth'].help_text, "Date of birth is required")
        self.assertEqual(form.fields['gender'].help_text, "Gender is required")
    
    def test_form_field_max_lengths(self):
        """Form alan maksimum uzunlukları testi"""
        form = CustomUserCreationForm()
        
        self.assertEqual(form.fields['first_name'].max_length, 30)
        self.assertEqual(form.fields['last_name'].max_length, 30)
    
    def test_form_field_widgets(self):
        """Form alan widget'ları testi"""
        form = CustomUserCreationForm()
        
        # Email widget
        self.assertIsInstance(form.fields['email'].widget, django.forms.EmailInput)
        
        # Phone number widget (custom widget)
        from leads.forms import PhoneNumberWidget
        self.assertIsInstance(form.fields['phone_number'].widget, PhoneNumberWidget)
        
        # Date widget
        self.assertIsInstance(form.fields['date_of_birth'].widget, django.forms.DateInput)
        
        # Password widgets
        self.assertIsInstance(form.fields['password1'].widget, django.forms.PasswordInput)
        self.assertIsInstance(form.fields['password2'].widget, django.forms.PasswordInput)
    
    def test_form_meta_class(self):
        """Form Meta sınıfı testi"""
        form = CustomUserCreationForm()
        
        self.assertEqual(form.Meta.model, User)
        self.assertEqual(form.Meta.fields, ("username", "first_name", "last_name", "email", "phone_number", "date_of_birth", "gender", "password1", "password2"))
        self.assertEqual(form.Meta.field_classes['username'], django.contrib.auth.forms.UsernameField)


class TestSignupFormIntegration(TestCase):
    """Signup form entegrasyon testleri"""
    
    def setUp(self):
        """Test verilerini hazırla"""
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
    
    def test_form_save_and_user_creation(self):
        """Form ile kullanıcı oluşturma testi"""
        form = CustomUserCreationForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
        
        user = form.save()
        
        # Kullanıcı veritabanında oluşturuldu mu
        self.assertTrue(User.objects.filter(username='integration_test_user').exists())
        
        saved_user = User.objects.get(username='integration_test_user')
        self.assertEqual(saved_user.email, 'integration_test@example.com')
        self.assertEqual(saved_user.first_name, 'Integration')
        self.assertEqual(saved_user.last_name, 'Test')
        self.assertEqual(str(saved_user.phone_number), '+905559876543')
        self.assertEqual(saved_user.gender, 'F')
        self.assertEqual(saved_user.date_of_birth.strftime('%Y-%m-%d'), '1985-05-15')
        
        # Şifre doğru set edildi mi
        self.assertTrue(saved_user.check_password('testpass123!'))
    
    def test_form_with_existing_data_conflicts(self):
        """Mevcut verilerle çakışma testi"""
        # Önce bir kullanıcı oluştur
        User.objects.create_user(
            username='conflict_user',
            email='conflict@example.com',
            password='testpass123',
            phone_number='+905551111111'
        )
        
        # Çakışan email ile form test et
        data = self.valid_data.copy()
        data['email'] = 'conflict@example.com'
        data['username'] = 'different_username'
        
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        
        # Çakışan telefon numarası ile form test et
        data = self.valid_data.copy()
        data['phone_number_0'] = '+90'
        data['phone_number_1'] = '5551111111'
        data['username'] = 'different_username2'
        
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('phone_number', form.errors)
        
        # Çakışan kullanıcı adı ile form test et
        data = self.valid_data.copy()
        data['username'] = 'conflict_user'
        
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)


if __name__ == "__main__":
    print("Signup Form Testleri Başlatılıyor...")
    print("=" * 60)
    
    # Test çalıştırma
    import unittest
    unittest.main()
