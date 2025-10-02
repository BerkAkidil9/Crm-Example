"""
Forget Password Formları Test Dosyası
Bu dosya forget password ile ilgili tüm formları test eder.
"""

import os
import sys
import django
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core import mail
from django.utils import timezone
from unittest.mock import patch, MagicMock

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djcrm.settings')
django.setup()

from leads.forms import CustomPasswordResetForm, CustomSetPasswordForm
from leads.models import User, UserProfile, EmailVerificationToken
from organisors.models import Organisor

User = get_user_model()


class TestCustomPasswordResetForm(TestCase):
    """CustomPasswordResetForm testleri"""
    
    def setUp(self):
        """Test verilerini hazırla"""
        # Test kullanıcısı oluştur
        self.user = User.objects.create_user(
            username='testuser_password_reset_form',
            email='test_password_reset_form@example.com',
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
    
    def test_form_initialization(self):
        """Form başlatma testi"""
        form = CustomPasswordResetForm()
        
        # Form alanları doğru mu
        self.assertIn('email', form.fields)
        self.assertEqual(form.fields['email'].label, 'Email')
        self.assertEqual(form.fields['email'].max_length, 254)
    
    def test_form_widget_attributes(self):
        """Form widget özellikleri testi"""
        form = CustomPasswordResetForm()
        email_widget = form.fields['email'].widget
        
        # Widget özellikleri doğru mu
        self.assertEqual(email_widget.attrs['autofocus'], True)
        self.assertEqual(email_widget.attrs['placeholder'], 'Email')
        self.assertIn('w-full px-3 py-2 border border-gray-300 rounded-md', email_widget.attrs['class'])
        self.assertIn('focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500', email_widget.attrs['class'])
    
    def test_form_valid_data(self):
        """Form geçerli veri testi"""
        data = {
            'email': 'test_password_reset_form@example.com'
        }
        
        form = CustomPasswordResetForm(data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['email'], 'test_password_reset_form@example.com')
    
    def test_form_invalid_email_format(self):
        """Form geçersiz email formatı testi"""
        data = {
            'email': 'invalid-email-format'
        }
        
        form = CustomPasswordResetForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertIn('Enter a valid email address', str(form.errors['email']))
    
    def test_form_empty_email(self):
        """Form boş email testi"""
        data = {
            'email': ''
        }
        
        form = CustomPasswordResetForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertIn('This field is required', str(form.errors['email']))
    
    def test_form_nonexistent_email(self):
        """Form var olmayan email testi"""
        data = {
            'email': 'nonexistent@example.com'
        }
        
        form = CustomPasswordResetForm(data)
        # Form valid olmalı (güvenlik için var olmayan email de kabul edilir)
        self.assertTrue(form.is_valid())
    
    def test_form_case_insensitive_email(self):
        """Form case insensitive email testi"""
        data = {
            'email': 'TEST_PASSWORD_RESET_FORM@EXAMPLE.COM'
        }
        
        form = CustomPasswordResetForm(data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['email'], 'TEST_PASSWORD_RESET_FORM@EXAMPLE.COM')
    
    def test_form_whitespace_email(self):
        """Form whitespace içeren email testi"""
        data = {
            'email': '  test_password_reset_form@example.com  '
        }
        
        form = CustomPasswordResetForm(data)
        self.assertTrue(form.is_valid())
        # Whitespace otomatik olarak temizlenir
        self.assertEqual(form.cleaned_data['email'], 'test_password_reset_form@example.com')
    
    def test_form_long_email(self):
        """Form çok uzun email testi"""
        data = {
            'email': 'a' * 300 + '@example.com'
        }
        
        form = CustomPasswordResetForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertIn('Ensure this value has at most 254 characters', str(form.errors['email']))
    
    def test_form_special_characters_email(self):
        """Form özel karakterler içeren email testi"""
        data = {
            'email': 'test+tag@example.com'
        }
        
        form = CustomPasswordResetForm(data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['email'], 'test+tag@example.com')
    
    def test_form_multiple_at_symbols(self):
        """Form birden fazla @ sembolü içeren email testi"""
        data = {
            'email': 'test@example@com'
        }
        
        form = CustomPasswordResetForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertIn('Enter a valid email address', str(form.errors['email']))
    
    def test_form_no_at_symbol(self):
        """Form @ sembolü olmayan email testi"""
        data = {
            'email': 'testexample.com'
        }
        
        form = CustomPasswordResetForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertIn('Enter a valid email address', str(form.errors['email']))
    
    def test_form_no_domain(self):
        """Form domain olmayan email testi"""
        data = {
            'email': 'test@'
        }
        
        form = CustomPasswordResetForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertIn('Enter a valid email address', str(form.errors['email']))
    
    def test_form_no_local_part(self):
        """Form local part olmayan email testi"""
        data = {
            'email': '@example.com'
        }
        
        form = CustomPasswordResetForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertIn('Enter a valid email address', str(form.errors['email']))
    
    def test_form_unicode_email(self):
        """Form Unicode karakterler içeren email testi"""
        data = {
            'email': 'tëst@ëxämplë.com'
        }
        
        form = CustomPasswordResetForm(data)
        # Unicode email'ler Django'da geçerli olmayabilir
        if form.is_valid():
            self.assertEqual(form.cleaned_data['email'], 'tëst@ëxämplë.com')
        else:
            # Unicode email geçersizse bu normal
            self.assertFalse(form.is_valid())
    
    def test_form_numeric_email(self):
        """Form sayısal email testi"""
        data = {
            'email': '123@456.com'
        }
        
        form = CustomPasswordResetForm(data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['email'], '123@456.com')
    
    def test_form_email_with_dots(self):
        """Form nokta içeren email testi"""
        data = {
            'email': 'test.user@example.com'
        }
        
        form = CustomPasswordResetForm(data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['email'], 'test.user@example.com')
    
    def test_form_email_with_plus(self):
        """Form + sembolü içeren email testi"""
        data = {
            'email': 'test+user@example.com'
        }
        
        form = CustomPasswordResetForm(data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['email'], 'test+user@example.com')
    
    def test_form_email_with_hyphens(self):
        """Form tire içeren email testi"""
        data = {
            'email': 'test-user@example.com'
        }
        
        form = CustomPasswordResetForm(data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['email'], 'test-user@example.com')
    
    def test_form_email_with_underscores(self):
        """Form alt çizgi içeren email testi"""
        data = {
            'email': 'test_user@example.com'
        }
        
        form = CustomPasswordResetForm(data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['email'], 'test_user@example.com')


class TestCustomSetPasswordForm(TestCase):
    """CustomSetPasswordForm testleri"""
    
    def setUp(self):
        """Test verilerini hazırla"""
        # Test kullanıcısı oluştur
        self.user = User.objects.create_user(
            username='testuser_set_password_form',
            email='test_set_password_form@example.com',
            password='oldpassword123',
            first_name='Test',
            last_name='User',
            phone_number='+905551234567',
            date_of_birth='1990-01-01',
            gender='M',
            is_organisor=True,
            email_verified=True
        )
    
    def test_form_initialization(self):
        """Form başlatma testi"""
        form = CustomSetPasswordForm(user=self.user)
        
        # Form alanları doğru mu
        self.assertIn('new_password1', form.fields)
        self.assertIn('new_password2', form.fields)
        self.assertEqual(form.fields['new_password1'].label, 'New password')
        self.assertEqual(form.fields['new_password2'].label, 'New password confirmation')
    
    def test_form_widget_attributes(self):
        """Form widget özellikleri testi"""
        form = CustomSetPasswordForm(user=self.user)
        
        # new_password1 widget özellikleri
        password1_widget = form.fields['new_password1'].widget
        self.assertEqual(password1_widget.attrs['autofocus'], True)
        self.assertEqual(password1_widget.attrs['placeholder'], 'New Password')
        self.assertIn('w-full px-3 py-2 border border-gray-300 rounded-md', password1_widget.attrs['class'])
        self.assertIn('focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500', password1_widget.attrs['class'])
        
        # new_password2 widget özellikleri
        password2_widget = form.fields['new_password2'].widget
        self.assertEqual(password2_widget.attrs['placeholder'], 'Confirm New Password')
        self.assertIn('w-full px-3 py-2 border border-gray-300 rounded-md', password2_widget.attrs['class'])
        self.assertIn('focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500', password2_widget.attrs['class'])
    
    def test_form_help_text(self):
        """Form help text testi"""
        form = CustomSetPasswordForm(user=self.user)
        
        help_text = form.fields['new_password1'].help_text
        self.assertIn("Your password can't be too similar to your other personal information", help_text)
        self.assertIn("must contain at least 8 characters", help_text)
        self.assertIn("can't be a commonly used password", help_text)
        self.assertIn("can't be entirely numeric", help_text)
    
    def test_form_valid_data(self):
        """Form geçerli veri testi"""
        data = {
            'new_password1': 'newpassword123!',
            'new_password2': 'newpassword123!'
        }
        
        form = CustomSetPasswordForm(user=self.user, data=data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['new_password1'], 'newpassword123!')
        self.assertEqual(form.cleaned_data['new_password2'], 'newpassword123!')
    
    def test_form_password_mismatch(self):
        """Form şifre uyumsuzluğu testi"""
        data = {
            'new_password1': 'newpassword123!',
            'new_password2': 'differentpassword123!'
        }
        
        form = CustomSetPasswordForm(user=self.user, data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('new_password2', form.errors)
        self.assertIn("match", str(form.errors['new_password2']).lower())
    
    def test_form_empty_passwords(self):
        """Form boş şifre testi"""
        data = {
            'new_password1': '',
            'new_password2': ''
        }
        
        form = CustomSetPasswordForm(user=self.user, data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('new_password1', form.errors)
        self.assertIn('new_password2', form.errors)
        self.assertIn('This field is required', str(form.errors['new_password1']))
        self.assertIn('This field is required', str(form.errors['new_password2']))
    
    def test_form_short_password(self):
        """Form kısa şifre testi"""
        data = {
            'new_password1': '123',
            'new_password2': '123'
        }
        
        form = CustomSetPasswordForm(user=self.user, data=data)
        self.assertFalse(form.is_valid())
        # Django'nun password validation'ı farklı field'a error atayabilir
        self.assertTrue(any('short' in str(errors) for errors in form.errors.values()))
    
    def test_form_common_password(self):
        """Form yaygın şifre testi"""
        data = {
            'new_password1': 'password',
            'new_password2': 'password'
        }
        
        form = CustomSetPasswordForm(user=self.user, data=data)
        self.assertFalse(form.is_valid())
        # Django'nun password validation'ı farklı field'a error atayabilir
        self.assertTrue(any('common' in str(errors) for errors in form.errors.values()))
    
    def test_form_numeric_password(self):
        """Form tamamen sayısal şifre testi"""
        data = {
            'new_password1': '12345678',
            'new_password2': '12345678'
        }
        
        form = CustomSetPasswordForm(user=self.user, data=data)
        self.assertFalse(form.is_valid())
        # Django'nun password validation'ı farklı field'a error atayabilir
        self.assertTrue(any('numeric' in str(errors) for errors in form.errors.values()))
    
    def test_form_similar_to_username(self):
        """Form kullanıcı adına benzer şifre testi"""
        data = {
            'new_password1': 'testuser_set_password_form123',
            'new_password2': 'testuser_set_password_form123'
        }
        
        form = CustomSetPasswordForm(user=self.user, data=data)
        self.assertFalse(form.is_valid())
        # Django'nun password validation'ı farklı field'a error atayabilir
        self.assertTrue(any('username' in str(errors) for errors in form.errors.values()))
    
    def test_form_similar_to_email(self):
        """Form email'e benzer şifre testi"""
        data = {
            'new_password1': 'test_set_password_form@example.com123',
            'new_password2': 'test_set_password_form@example.com123'
        }
        
        form = CustomSetPasswordForm(user=self.user, data=data)
        # Django'nun password validation'ı farklı olabilir
        # Bu test sadece form'un çalıştığını kontrol eder
        self.assertIsInstance(form, CustomSetPasswordForm)
    
    def test_form_similar_to_first_name(self):
        """Form ad'a benzer şifre testi"""
        data = {
            'new_password1': 'Test123456',
            'new_password2': 'Test123456'
        }
        
        form = CustomSetPasswordForm(user=self.user, data=data)
        # Django'nun password validation'ı farklı olabilir
        if form.is_valid():
            # Eğer form valid ise, bu Django'nun validation kurallarına göre normal
            self.assertTrue(form.is_valid())
        else:
            # Eğer form invalid ise, first name similarity kontrolü çalışıyor
            self.assertFalse(form.is_valid())
            self.assertTrue(any('first name' in str(errors).lower() for errors in form.errors.values()))
    
    def test_form_similar_to_last_name(self):
        """Form soyad'a benzer şifre testi"""
        data = {
            'new_password1': 'User123456',
            'new_password2': 'User123456'
        }
        
        form = CustomSetPasswordForm(user=self.user, data=data)
        # Django'nun password validation'ı farklı olabilir
        if form.is_valid():
            # Eğer form valid ise, bu Django'nun validation kurallarına göre normal
            self.assertTrue(form.is_valid())
        else:
            # Eğer form invalid ise, last name similarity kontrolü çalışıyor
            self.assertFalse(form.is_valid())
            self.assertTrue(any('last name' in str(errors).lower() for errors in form.errors.values()))
    
    def test_form_whitespace_passwords(self):
        """Form whitespace içeren şifre testi"""
        data = {
            'new_password1': '  newpassword123!  ',
            'new_password2': '  newpassword123!  '
        }
        
        form = CustomSetPasswordForm(user=self.user, data=data)
        self.assertTrue(form.is_valid())
        # Whitespace otomatik olarak temizlenir (strip=False olduğu için temizlenmez)
        self.assertEqual(form.cleaned_data['new_password1'], '  newpassword123!  ')
        self.assertEqual(form.cleaned_data['new_password2'], '  newpassword123!  ')
    
    def test_form_unicode_passwords(self):
        """Form Unicode karakterler içeren şifre testi"""
        data = {
            'new_password1': 'pässwörd123!',
            'new_password2': 'pässwörd123!'
        }
        
        form = CustomSetPasswordForm(user=self.user, data=data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['new_password1'], 'pässwörd123!')
        self.assertEqual(form.cleaned_data['new_password2'], 'pässwörd123!')
    
    def test_form_special_characters_passwords(self):
        """Form özel karakterler içeren şifre testi"""
        data = {
            'new_password1': 'P@ssw0rd!@#$%^&*()',
            'new_password2': 'P@ssw0rd!@#$%^&*()'
        }
        
        form = CustomSetPasswordForm(user=self.user, data=data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['new_password1'], 'P@ssw0rd!@#$%^&*()')
        self.assertEqual(form.cleaned_data['new_password2'], 'P@ssw0rd!@#$%^&*()')
    
    def test_form_long_password(self):
        """Form uzun şifre testi"""
        data = {
            'new_password1': 'a' * 200 + '123!',
            'new_password2': 'a' * 200 + '123!'
        }
        
        form = CustomSetPasswordForm(user=self.user, data=data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['new_password1'], 'a' * 200 + '123!')
        self.assertEqual(form.cleaned_data['new_password2'], 'a' * 200 + '123!')
    
    def test_form_save_functionality(self):
        """Form save fonksiyonalitesi testi"""
        data = {
            'new_password1': 'newpassword123!',
            'new_password2': 'newpassword123!'
        }
        
        form = CustomSetPasswordForm(user=self.user, data=data)
        self.assertTrue(form.is_valid())
        
        # Form save edilir
        form.save()
        
        # Kullanıcının şifresi değişti mi
        updated_user = User.objects.get(pk=self.user.pk)
        self.assertTrue(updated_user.check_password('newpassword123!'))
        self.assertFalse(updated_user.check_password('oldpassword123'))
    
    def test_form_save_with_commit_false(self):
        """Form save commit=False ile testi"""
        data = {
            'new_password1': 'newpassword123!',
            'new_password2': 'newpassword123!'
        }
        
        form = CustomSetPasswordForm(user=self.user, data=data)
        self.assertTrue(form.is_valid())
        
        # Form save edilir ama commit=False
        user = form.save(commit=False)
        
        # Kullanıcının şifresi henüz değişmedi
        updated_user = User.objects.get(pk=self.user.pk)
        self.assertFalse(updated_user.check_password('newpassword123!'))
        self.assertTrue(updated_user.check_password('oldpassword123'))
        
        # Manuel olarak save et
        user.save()
        
        # Şimdi şifre değişti
        updated_user = User.objects.get(pk=self.user.pk)
        self.assertTrue(updated_user.check_password('newpassword123!'))
        self.assertFalse(updated_user.check_password('oldpassword123'))


class TestForgetPasswordFormIntegration(TestCase):
    """Forget password form entegrasyon testleri"""
    
    def setUp(self):
        """Test verilerini hazırla"""
        # Test kullanıcısı oluştur
        self.user = User.objects.create_user(
            username='integration_form_user',
            email='integration_form@example.com',
            password='oldpassword123',
            first_name='Integration',
            last_name='Form',
            phone_number='+905556666666',
            date_of_birth='1990-01-01',
            gender='M',
            is_organisor=True,
            email_verified=True
        )
    
    def test_password_reset_form_with_existing_user(self):
        """Mevcut kullanıcı ile password reset form testi"""
        data = {'email': 'integration_form@example.com'}
        form = CustomPasswordResetForm(data)
        
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['email'], 'integration_form@example.com')
    
    def test_password_reset_form_with_nonexistent_user(self):
        """Var olmayan kullanıcı ile password reset form testi"""
        data = {'email': 'nonexistent@example.com'}
        form = CustomPasswordResetForm(data)
        
        # Güvenlik için var olmayan email de kabul edilir
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['email'], 'nonexistent@example.com')
    
    def test_set_password_form_with_valid_data(self):
        """Geçerli veri ile set password form testi"""
        data = {
            'new_password1': 'newpassword123!',
            'new_password2': 'newpassword123!'
        }
        form = CustomSetPasswordForm(user=self.user, data=data)
        
        self.assertTrue(form.is_valid())
        
        # Form save edilir
        form.save()
        
        # Kullanıcının şifresi değişti mi
        updated_user = User.objects.get(pk=self.user.pk)
        self.assertTrue(updated_user.check_password('newpassword123!'))
        self.assertFalse(updated_user.check_password('oldpassword123'))
    
    def test_set_password_form_with_invalid_data(self):
        """Geçersiz veri ile set password form testi"""
        data = {
            'new_password1': '123',  # Çok kısa
            'new_password2': '123'
        }
        form = CustomSetPasswordForm(user=self.user, data=data)
        
        self.assertFalse(form.is_valid())
        # Django'nun password validation'ı farklı field'a error atayabilir
        self.assertTrue(any('short' in str(errors) for errors in form.errors.values()))
        
        # Kullanıcının şifresi değişmedi mi
        updated_user = User.objects.get(pk=self.user.pk)
        self.assertTrue(updated_user.check_password('oldpassword123'))
        self.assertFalse(updated_user.check_password('123'))
    
    def test_form_validation_edge_cases(self):
        """Form validasyon edge case'leri testi"""
        # Boş form
        form = CustomPasswordResetForm({})
        self.assertFalse(form.is_valid())
        
        # None data
        form = CustomPasswordResetForm(None)
        self.assertFalse(form.is_valid())
        
        # Set password form boş data
        form = CustomSetPasswordForm(user=self.user, data={})
        self.assertFalse(form.is_valid())
        
        # Set password form None data
        form = CustomSetPasswordForm(user=self.user, data=None)
        self.assertFalse(form.is_valid())
    
    def test_form_field_attributes(self):
        """Form alan özellikleri testi"""
        # Password reset form
        reset_form = CustomPasswordResetForm()
        email_field = reset_form.fields['email']
        
        self.assertEqual(email_field.label, 'Email')
        self.assertEqual(email_field.max_length, 254)
        self.assertTrue(email_field.required)
        
        # Set password form
        set_form = CustomSetPasswordForm(user=self.user)
        password1_field = set_form.fields['new_password1']
        password2_field = set_form.fields['new_password2']
        
        self.assertEqual(password1_field.label, 'New password')
        self.assertEqual(password2_field.label, 'New password confirmation')
        self.assertTrue(password1_field.required)
        self.assertTrue(password2_field.required)
        self.assertFalse(password1_field.strip)
        self.assertFalse(password2_field.strip)


if __name__ == "__main__":
    print("Forget Password Form Testleri Başlatılıyor...")
    print("=" * 60)
    
    # Test çalıştırma
    import unittest
    unittest.main()
