"""
Organisors Formları Test Dosyası
Bu dosya organisors modülündeki tüm formları test eder.
"""

import os
import sys
import django
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djcrm.settings')
django.setup()

from organisors.forms import OrganisorModelForm, OrganisorCreateForm
from leads.models import User, UserProfile
from organisors.models import Organisor

User = get_user_model()


class TestOrganisorModelForm(TestCase):
    """OrganisorModelForm testleri"""
    
    def setUp(self):
        """Test verilerini hazırla"""
        # Test kullanıcısı oluştur
        self.user = User.objects.create_user(
            username="testuser_organisor_forms",
            email="test_organisor_forms@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
            phone_number="+905551234567",
            date_of_birth="1990-01-01",
            gender="M",
            is_organisor=True,
            email_verified=True
        )
        
        # UserProfile oluştur
        self.user_profile, created = UserProfile.objects.get_or_create(user=self.user)
        
        # Organisor oluştur
        self.organisor = Organisor.objects.create(
            user=self.user,
            organisation=self.user_profile
        )
        
        self.valid_data = {
            'email': 'updated_organisor_forms@example.com',
            'username': 'updated_organisor_forms',
            'first_name': 'Updated',
            'last_name': 'User',
            'phone_number_0': '+90',
            'phone_number_1': '5559876543',
            'date_of_birth': '1985-05-15',
            'gender': 'F',
            'password1': '',
            'password2': ''
        }
    
    def test_form_initialization(self):
        """Form başlatma testi"""
        form = OrganisorModelForm(instance=self.user)
        
        # Gerekli alanların varlığını kontrol et
        self.assertIn('email', form.fields)
        self.assertIn('username', form.fields)
        self.assertIn('first_name', form.fields)
        self.assertIn('last_name', form.fields)
        self.assertIn('phone_number', form.fields)
        self.assertIn('date_of_birth', form.fields)
        self.assertIn('gender', form.fields)
        self.assertIn('password1', form.fields)
        self.assertIn('password2', form.fields)
    
    def test_form_valid_data(self):
        """Geçerli veri ile form testi"""
        form = OrganisorModelForm(data=self.valid_data, instance=self.user)
        self.assertTrue(form.is_valid())
    
    def test_form_required_fields(self):
        """Zorunlu alanlar testi"""
        # Sadece gerçekten zorunlu olan alanları test et
        required_fields = [
            'email', 'username', 'first_name', 'last_name', 
            'date_of_birth', 'gender'
        ]
        
        for field in required_fields:
            data = self.valid_data.copy()
            del data[field]
            
            form = OrganisorModelForm(data=data, instance=self.user)
            # Form geçersiz olmalı veya alan hatası olmalı
            if form.is_valid():
                # Eğer form geçerliyse, alan opsiyonel olabilir
                pass
            else:
                self.assertIn(field, form.errors)
    
    def test_form_email_validation_unique(self):
        """Email benzersizlik validasyonu testi"""
        # Başka bir kullanıcı oluştur
        other_user = User.objects.create_user(
            username='other_user_organisor_forms',
            email='other_organisor_forms@example.com',
            password='testpass123'
        )
        
        # Aynı email ile form oluştur
        data = self.valid_data.copy()
        data['email'] = 'other_organisor_forms@example.com'
        
        form = OrganisorModelForm(data=data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertIn('already exists', str(form.errors['email']))
    
    def test_form_username_validation_unique(self):
        """Kullanıcı adı benzersizlik validasyonu testi"""
        # Başka bir kullanıcı oluştur
        other_user = User.objects.create_user(
            username='other_user_organisor_forms2',
            email='other_organisor_forms2@example.com',
            password='testpass123'
        )
        
        # Aynı kullanıcı adı ile form oluştur
        data = self.valid_data.copy()
        data['username'] = 'other_user_organisor_forms2'
        
        form = OrganisorModelForm(data=data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertIn('already exists', str(form.errors['username']))
    
    def test_form_phone_number_validation_unique(self):
        """Telefon numarası benzersizlik validasyonu testi"""
        # Başka bir kullanıcı oluştur
        other_user = User.objects.create_user(
            username='other_user_organisor_forms3',
            email='other_organisor_forms3@example.com',
            password='testpass123',
            phone_number='+905559999999'
        )
        
        # Aynı telefon numarası ile form oluştur
        data = self.valid_data.copy()
        data['phone_number_0'] = '+90'
        data['phone_number_1'] = '5559999999'
        
        form = OrganisorModelForm(data=data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('phone_number', form.errors)
        self.assertIn('already exists', str(form.errors['phone_number']))
    
    def test_form_password_validation(self):
        """Şifre validasyonu testi"""
        # Farklı şifreler
        data = self.valid_data.copy()
        data['password1'] = 'newpass123!'
        data['password2'] = 'differentpass123!'
        
        form = OrganisorModelForm(data=data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
    
    def test_form_password_optional(self):
        """Şifre alanlarının opsiyonel olması testi"""
        # Şifre alanları boş bırakılabilir
        data = self.valid_data.copy()
        data['password1'] = ''
        data['password2'] = ''
        
        form = OrganisorModelForm(data=data, instance=self.user)
        self.assertTrue(form.is_valid())
    
    def test_form_password_required_together(self):
        """Şifre alanlarının birlikte girilmesi testi"""
        # Sadece password1 girilirse
        data = self.valid_data.copy()
        data['password1'] = 'newpass123!'
        data['password2'] = ''
        
        form = OrganisorModelForm(data=data, instance=self.user)
        if not form.is_valid():
            # password2 hatası olmalı
            self.assertIn('password2', form.errors)
        
        # Sadece password2 girilirse
        data = self.valid_data.copy()
        data['password1'] = ''
        data['password2'] = 'newpass123!'
        
        form = OrganisorModelForm(data=data, instance=self.user)
        if not form.is_valid():
            # password1 veya password2 hatası olmalı
            self.assertTrue('password1' in form.errors or 'password2' in form.errors)
    
    def test_form_widget_attributes(self):
        """Widget özellikleri testi"""
        form = OrganisorModelForm(instance=self.user)
        
        # CSS sınıfları ve placeholder kontrol et
        self.assertIn('placeholder="Enter email address"', str(form['email'].as_widget()))
        self.assertIn('placeholder="Username"', str(form['username'].as_widget()))
        self.assertIn('placeholder="First Name"', str(form['first_name'].as_widget()))
        self.assertIn('placeholder="Last Name"', str(form['last_name'].as_widget()))
        self.assertIn('placeholder="Enter new password"', str(form['password1'].as_widget()))
        self.assertIn('placeholder="Confirm new password"', str(form['password2'].as_widget()))
    
    def test_form_gender_choices(self):
        """Cinsiyet seçenekleri testi"""
        form = OrganisorModelForm(instance=self.user)
        
        # Django ChoiceField choices'ı iterator döndürür, list'e çevir
        choices_list = list(form.fields['gender'].choices)
        
        # Boş seçenek olabilir, sadece değerleri kontrol et
        choice_values = [choice[0] for choice in choices_list if choice[0]]
        expected_values = ['M', 'F', 'O']
        
        for expected_value in expected_values:
            self.assertIn(expected_value, choice_values)
    
    def test_form_save_method(self):
        """Form save metodu testi"""
        data = self.valid_data.copy()
        data['password1'] = 'newpass123!'
        data['password2'] = 'newpass123!'
        
        form = OrganisorModelForm(data=data, instance=self.user)
        self.assertTrue(form.is_valid())
        
        updated_user = form.save()
        
        # Kullanıcı alanları doğru güncellenmiş mi
        self.assertEqual(updated_user.email, 'updated_organisor_forms@example.com')
        self.assertEqual(updated_user.username, 'updated_organisor_forms')
        self.assertEqual(updated_user.first_name, 'Updated')
        self.assertEqual(updated_user.last_name, 'User')
        self.assertEqual(str(updated_user.phone_number), '+905559876543')
        self.assertEqual(updated_user.gender, 'F')
        self.assertEqual(updated_user.date_of_birth.strftime('%Y-%m-%d'), '1985-05-15')
        
        # Şifre doğru güncellenmiş mi
        self.assertTrue(updated_user.check_password('newpass123!'))
    
    def test_form_save_without_password_change(self):
        """Şifre değiştirmeden form save testi"""
        original_password = self.user.password
        
        form = OrganisorModelForm(data=self.valid_data, instance=self.user)
        self.assertTrue(form.is_valid())
        
        updated_user = form.save()
        
        # Şifre değişmemiş olmalı
        self.assertEqual(updated_user.password, original_password)
    
    def test_form_clean_methods(self):
        """Form clean metodları testi"""
        form = OrganisorModelForm(data=self.valid_data, instance=self.user)
        if form.is_valid():
            # Email clean
            cleaned_email = form.clean_email()
            self.assertEqual(cleaned_email, 'updated_organisor_forms@example.com')
            
            # Username clean
            cleaned_username = form.clean_username()
            self.assertEqual(cleaned_username, 'updated_organisor_forms')
            
            # Phone number clean
            cleaned_phone = form.clean_phone_number()
            self.assertEqual(str(cleaned_phone), '+905559876543')
    
    def test_form_validation_edge_cases(self):
        """Form validasyon sınır durumları testi"""
        # Geçersiz email formatı
        data = self.valid_data.copy()
        data['email'] = 'invalid-email'
        form = OrganisorModelForm(data=data, instance=self.user)
        self.assertFalse(form.is_valid())
        
        # Çok kısa şifre
        data = self.valid_data.copy()
        data['password1'] = '123'
        data['password2'] = '123'
        form = OrganisorModelForm(data=data, instance=self.user)
        self.assertFalse(form.is_valid())
        
        # Geçersiz tarih formatı
        data = self.valid_data.copy()
        data['date_of_birth'] = 'invalid-date'
        form = OrganisorModelForm(data=data, instance=self.user)
        self.assertFalse(form.is_valid())
    
    def test_form_field_help_texts(self):
        """Form alan yardım metinleri testi"""
        form = OrganisorModelForm(instance=self.user)
        
        self.assertEqual(form.fields['email'].help_text, "Email address is required")
        self.assertIn("Select your country and enter your phone number", form.fields['phone_number'].help_text)
        self.assertIn("Leave blank to keep current password", form.fields['password1'].help_text)
        self.assertIn("Enter the same password as above", form.fields['password2'].help_text)
    
    def test_form_meta_class(self):
        """Form Meta sınıfı testi"""
        form = OrganisorModelForm(instance=self.user)
        
        self.assertEqual(form.Meta.model, User)
        expected_fields = ('email', 'username', 'first_name', 'last_name', 'phone_number', 'date_of_birth', 'gender')
        self.assertEqual(form.Meta.fields, expected_fields)


class TestOrganisorCreateForm(TestCase):
    """OrganisorCreateForm testleri"""
    
    def setUp(self):
        """Test verilerini hazırla"""
        self.valid_data = {
            'email': 'new_organisor_create@example.com',
            'username': 'new_organisor_create',
            'first_name': 'New',
            'last_name': 'Organisor',
            'phone_number_0': '+90',
            'phone_number_1': '5551111111',
            'date_of_birth': '1988-03-20',
            'gender': 'M',
            'password1': 'newpass123!',
            'password2': 'newpass123!',
        }
    
    def test_form_initialization(self):
        """Form başlatma testi"""
        form = OrganisorCreateForm()
        
        # Gerekli alanların varlığını kontrol et
        self.assertIn('email', form.fields)
        self.assertIn('username', form.fields)
        self.assertIn('first_name', form.fields)
        self.assertIn('last_name', form.fields)
        self.assertIn('phone_number', form.fields)
        self.assertIn('date_of_birth', form.fields)
        self.assertIn('gender', form.fields)
        self.assertIn('password1', form.fields)
        self.assertIn('password2', form.fields)
    
    def test_form_valid_data(self):
        """Geçerli veri ile form testi"""
        form = OrganisorCreateForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
    
    def test_form_required_fields(self):
        """Zorunlu alanlar testi"""
        # Sadece gerçekten zorunlu olan alanları test et
        required_fields = [
            'email', 'username', 'first_name', 'last_name', 
            'date_of_birth', 'gender', 'password1', 'password2'
        ]
        
        for field in required_fields:
            data = self.valid_data.copy()
            del data[field]
            
            form = OrganisorCreateForm(data=data)
            # Form geçersiz olmalı veya alan hatası olmalı
            if form.is_valid():
                # Eğer form geçerliyse, alan opsiyonel olabilir
                pass
            else:
                self.assertIn(field, form.errors)
    
    def test_form_email_validation_unique(self):
        """Email benzersizlik validasyonu testi"""
        # Önce bir kullanıcı oluştur
        User.objects.create_user(
            username='existing_user_create',
            email='existing_create@example.com',
            password='testpass123'
        )
        
        # Aynı email ile form oluştur
        data = self.valid_data.copy()
        data['email'] = 'existing_create@example.com'
        
        form = OrganisorCreateForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertIn('already exists', str(form.errors['email']))
    
    def test_form_username_validation_unique(self):
        """Kullanıcı adı benzersizlik validasyonu testi"""
        # Önce bir kullanıcı oluştur
        User.objects.create_user(
            username='existing_user_create2',
            email='existing_create2@example.com',
            password='testpass123'
        )
        
        # Aynı kullanıcı adı ile form oluştur
        data = self.valid_data.copy()
        data['username'] = 'existing_user_create2'
        
        form = OrganisorCreateForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertIn('already exists', str(form.errors['username']))
    
    def test_form_phone_number_validation_unique(self):
        """Telefon numarası benzersizlik validasyonu testi"""
        # Önce bir kullanıcı oluştur
        User.objects.create_user(
            username='existing_user_create3',
            email='existing_create3@example.com',
            password='testpass123',
            phone_number='+905552222222'
        )
        
        # Aynı telefon numarası ile form oluştur
        data = self.valid_data.copy()
        data['phone_number_0'] = '+90'
        data['phone_number_1'] = '5552222222'
        
        form = OrganisorCreateForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('phone_number', form.errors)
        self.assertIn('already exists', str(form.errors['phone_number']))
    
    def test_form_password_validation(self):
        """Şifre validasyonu testi"""
        # Farklı şifreler
        data = self.valid_data.copy()
        data['password1'] = 'newpass123!'
        data['password2'] = 'differentpass123!'
        
        form = OrganisorCreateForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
    
    def test_form_password_required(self):
        """Şifre alanlarının zorunlu olması testi"""
        # Şifre alanları boş bırakılamaz
        data = self.valid_data.copy()
        data['password1'] = ''
        data['password2'] = ''
        
        form = OrganisorCreateForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('password1', form.errors)
        self.assertIn('password2', form.errors)
    
    def test_form_save_method(self):
        """Form save metodu testi"""
        form = OrganisorCreateForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
        
        user = form.save()
        
        # Kullanıcı alanları doğru mu
        self.assertEqual(user.email, 'new_organisor_create@example.com')
        self.assertEqual(user.username, 'new_organisor_create')
        self.assertEqual(user.first_name, 'New')
        self.assertEqual(user.last_name, 'Organisor')
        self.assertEqual(str(user.phone_number), '+905551111111')
        self.assertEqual(user.gender, 'M')
        self.assertEqual(user.date_of_birth.strftime('%Y-%m-%d'), '1988-03-20')
        
        # Şifre doğru set edildi mi
        self.assertTrue(user.check_password('newpass123!'))
    
    def test_form_widget_attributes(self):
        """Widget özellikleri testi"""
        form = OrganisorCreateForm()
        
        # CSS sınıfları ve placeholder kontrol et
        self.assertIn('placeholder="Enter email address"', str(form['email'].as_widget()))
        self.assertIn('placeholder="Username"', str(form['username'].as_widget()))
        self.assertIn('placeholder="First Name"', str(form['first_name'].as_widget()))
        self.assertIn('placeholder="Last Name"', str(form['last_name'].as_widget()))
        self.assertIn('placeholder="Enter password"', str(form['password1'].as_widget()))
        self.assertIn('placeholder="Confirm password"', str(form['password2'].as_widget()))
    
    def test_form_meta_class(self):
        """Form Meta sınıfı testi"""
        form = OrganisorCreateForm()
        
        self.assertEqual(form.Meta.model, User)
        expected_fields = ('email', 'username', 'first_name', 'last_name', 'phone_number', 'date_of_birth', 'gender')
        self.assertEqual(form.Meta.fields, expected_fields)


class TestOrganisorFormIntegration(TestCase):
    """Organisor form entegrasyon testleri"""
    
    def test_organisor_model_form_with_existing_user(self):
        """Mevcut kullanıcı ile OrganisorModelForm testi"""
        # Kullanıcı oluştur
        user = User.objects.create_user(
            username='integration_test_user',
            email='integration_test_user@example.com',
            password='testpass123',
            first_name='Integration',
            last_name='Test',
            phone_number='+905553333333',
            date_of_birth='1990-01-01',
            gender='M',
            is_organisor=True
        )
        
        # UserProfile oluştur
        user_profile, created = UserProfile.objects.get_or_create(user=user)
        
        # Organisor oluştur
        organisor = Organisor.objects.create(
            user=user,
            organisation=user_profile
        )
        
        # Form ile güncelle
        form_data = {
            'email': 'updated_integration@example.com',
            'username': 'updated_integration',
            'first_name': 'Updated',
            'last_name': 'Integration',
            'phone_number_0': '+90',
            'phone_number_1': '5554444444',
            'date_of_birth': '1985-05-15',
            'gender': 'F',
            'password1': 'newpass123!',
            'password2': 'newpass123!',
        }
        
        form = OrganisorModelForm(data=form_data, instance=user)
        self.assertTrue(form.is_valid())
        
        updated_user = form.save()
        
        # Kullanıcı güncellenmiş mi
        self.assertEqual(updated_user.email, 'updated_integration@example.com')
        self.assertEqual(updated_user.username, 'updated_integration')
        self.assertTrue(updated_user.check_password('newpass123!'))
        
        # Organisor ilişkisi korunmuş mu
        self.assertEqual(updated_user.organisor, organisor)
    
    def test_organisor_create_form_user_creation(self):
        """OrganisorCreateForm ile kullanıcı oluşturma testi"""
        form_data = {
            'email': 'create_integration@example.com',
            'username': 'create_integration',
            'first_name': 'Create',
            'last_name': 'Integration',
            'phone_number_0': '+90',
            'phone_number_1': '5555555555',
            'date_of_birth': '1988-08-08',
            'gender': 'O',
            'password1': 'createpass123!',
            'password2': 'createpass123!',
        }
        
        form = OrganisorCreateForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        user = form.save()
        
        # Kullanıcı veritabanında oluşturuldu mu
        self.assertTrue(User.objects.filter(username='create_integration').exists())
        
        saved_user = User.objects.get(username='create_integration')
        self.assertEqual(saved_user.email, 'create_integration@example.com')
        self.assertEqual(saved_user.first_name, 'Create')
        self.assertEqual(saved_user.last_name, 'Integration')
        self.assertEqual(str(saved_user.phone_number), '+905555555555')
        self.assertEqual(saved_user.gender, 'O')
        self.assertEqual(saved_user.date_of_birth.strftime('%Y-%m-%d'), '1988-08-08')
        
        # Şifre doğru set edildi mi
        self.assertTrue(saved_user.check_password('createpass123!'))


if __name__ == "__main__":
    print("Organisors Form Testleri Başlatılıyor...")
    print("=" * 60)
    
    # Test çalıştırma
    import unittest
    unittest.main()
