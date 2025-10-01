"""
Signup Modelleri Test Dosyası
Bu dosya signup ile ilgili tüm modelleri test eder.
"""

import os
import sys
import django
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta
import uuid

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djcrm.settings')
django.setup()

from leads.models import User, UserProfile, EmailVerificationToken
from organisors.models import Organisor


class TestUserModel(TestCase):
    """User modeli testleri"""
    
    def setUp(self):
        """Test verilerini hazırla"""
        self.user_data = {
            'username': 'testuser_model',
            'email': 'test_model@example.com',
            'password': 'testpass123!',
            'first_name': 'Test',
            'last_name': 'User',
            'phone_number': '+905551234567',
            'date_of_birth': datetime(1990, 1, 1).date(),
            'gender': 'M',
        }
    
    def test_user_creation(self):
        """Kullanıcı oluşturma testi"""
        user = User.objects.create_user(**self.user_data)
        
        self.assertEqual(user.username, 'testuser_model')
        self.assertEqual(user.email, 'test_model@example.com')
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User')
        self.assertEqual(user.phone_number, '+905551234567')
        self.assertEqual(user.date_of_birth, datetime(1990, 1, 1).date())
        self.assertEqual(user.gender, 'M')
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)
        self.assertTrue(user.is_active)
    
    def test_user_creation_with_organisor_flag(self):
        """Organisor bayrağı ile kullanıcı oluşturma testi"""
        user_data = self.user_data.copy()
        user_data['is_organisor'] = True
        
        user = User.objects.create_user(**user_data)
        
        self.assertTrue(user.is_organisor)
        self.assertFalse(user.is_agent)
    
    def test_user_creation_with_agent_flag(self):
        """Agent bayrağı ile kullanıcı oluşturma testi"""
        user_data = self.user_data.copy()
        user_data['username'] = 'testuser_agent_flag'
        user_data['email'] = 'test_agent_flag@example.com'
        user_data['is_agent'] = True
        user_data['is_organisor'] = False  # Explicitly set to False
        
        user = User.objects.create_user(**user_data)
        
        self.assertTrue(user.is_agent)
        self.assertFalse(user.is_organisor)
    
    def test_user_email_verification_default(self):
        """Email doğrulama varsayılan değeri testi"""
        user = User.objects.create_user(**self.user_data)
        
        self.assertFalse(user.email_verified)
    
    def test_user_email_verification_set(self):
        """Email doğrulama set etme testi"""
        user = User.objects.create_user(**self.user_data)
        user.email_verified = True
        user.save()
        
        updated_user = User.objects.get(pk=user.pk)
        self.assertTrue(updated_user.email_verified)
    
    def test_user_gender_choices(self):
        """Cinsiyet seçenekleri testi"""
        expected_choices = [
            ('M', 'Male'),
            ('F', 'Female'),
            ('O', 'Other'),
        ]
        
        self.assertEqual(User.GENDER_CHOICES, expected_choices)
    
    def test_user_str_method(self):
        """User __str__ metodu testi"""
        user = User.objects.create_user(**self.user_data)
        
        self.assertEqual(str(user), 'testuser_model')
    
    def test_user_get_full_name(self):
        """User get_full_name metodu testi"""
        user = User.objects.create_user(**self.user_data)
        
        self.assertEqual(user.get_full_name(), 'Test User')
    
    def test_user_get_short_name(self):
        """User get_short_name metodu testi"""
        user = User.objects.create_user(**self.user_data)
        
        self.assertEqual(user.get_short_name(), 'Test')
    
    def test_user_unique_constraints(self):
        """User benzersizlik kısıtlamaları testi"""
        # İlk kullanıcıyı oluştur
        User.objects.create_user(**self.user_data)
        
        # Aynı email ile ikinci kullanıcı oluşturmaya çalış
        with self.assertRaises(Exception):  # IntegrityError veya ValidationError
            User.objects.create_user(
                username='different_username',
                email='test_model@example.com',
                password='testpass123!'
            )
        
        # Aynı telefon numarası ile ikinci kullanıcı oluşturmaya çalış
        with self.assertRaises(Exception):  # IntegrityError veya ValidationError
            User.objects.create_user(
                username='different_username2',
                email='different@example.com',
                password='testpass123!',
                phone_number='+905551234567'
            )


class TestUserProfileModel(TestCase):
    """UserProfile modeli testleri"""
    
    def setUp(self):
        """Test verilerini hazırla"""
        self.user = User.objects.create_user(
            username='testuser_profile',
            email='test_profile@example.com',
            password='testpass123!'
        )
    
    def test_userprofile_creation(self):
        """UserProfile oluşturma testi"""
        # Test için yeni bir user oluştur
        test_user = User.objects.create_user(
            username='testuser_profile_creation',
            email='test_profile_creation@example.com',
            password='testpass123!'
        )
        # Signal nedeniyle UserProfile zaten oluşturulmuş olmalı
        profile = UserProfile.objects.get(user=test_user)
        
        self.assertEqual(profile.user, test_user)
        self.assertEqual(str(profile), 'testuser_profile_creation')
    
    def test_userprofile_get_or_create(self):
        """UserProfile get_or_create testi"""
        # Test için yeni bir user oluştur
        test_user = User.objects.create_user(
            username='testuser_profile_get_or_create',
            email='test_profile_get_or_create@example.com',
            password='testpass123!'
        )
        
        # Signal nedeniyle UserProfile zaten oluşturulmuş olmalı
        profile, created = UserProfile.objects.get_or_create(user=test_user)
        
        self.assertFalse(created)  # Signal nedeniyle zaten oluşturulmuş
        self.assertEqual(profile.user, test_user)
        
        # İkinci çağrı - oluşturulmamalı
        profile2, created2 = UserProfile.objects.get_or_create(user=test_user)
        
        self.assertFalse(created2)
        self.assertEqual(profile, profile2)
    
    def test_userprofile_unique_constraint(self):
        """UserProfile benzersizlik kısıtlaması testi"""
        # Test için yeni bir user oluştur
        test_user = User.objects.create_user(
            username='testuser_profile_unique',
            email='test_profile_unique@example.com',
            password='testpass123!'
        )
        
        # Signal nedeniyle UserProfile zaten oluşturulmuş olmalı
        self.assertTrue(UserProfile.objects.filter(user=test_user).exists())
        
        # Aynı kullanıcı için ikinci profile oluşturmaya çalış
        with self.assertRaises(Exception):  # IntegrityError
            UserProfile.objects.create(user=test_user)
    
    def test_userprofile_str_method(self):
        """UserProfile __str__ metodu testi"""
        # Test için yeni bir user oluştur
        test_user = User.objects.create_user(
            username='testuser_profile_str',
            email='test_profile_str@example.com',
            password='testpass123!'
        )
        # Signal nedeniyle UserProfile zaten oluşturulmuş olmalı
        profile = UserProfile.objects.get(user=test_user)
        
        self.assertEqual(str(profile), 'testuser_profile_str')


class TestEmailVerificationTokenModel(TestCase):
    """EmailVerificationToken modeli testleri"""
    
    def setUp(self):
        """Test verilerini hazırla"""
        self.user = User.objects.create_user(
            username='testuser_token',
            email='test_token@example.com',
            password='testpass123!'
        )
    
    def test_email_verification_token_creation(self):
        """EmailVerificationToken oluşturma testi"""
        token = EmailVerificationToken.objects.create(user=self.user)
        
        self.assertEqual(token.user, self.user)
        self.assertIsInstance(token.token, uuid.UUID)
        self.assertFalse(token.is_used)
        self.assertIsNotNone(token.created_at)
    
    def test_email_verification_token_str_method(self):
        """EmailVerificationToken __str__ metodu testi"""
        token = EmailVerificationToken.objects.create(user=self.user)
        
        expected_str = f"Verification token for {self.user.email}"
        self.assertEqual(str(token), expected_str)
    
    def test_email_verification_token_is_expired_false(self):
        """EmailVerificationToken süresi dolmamış testi"""
        token = EmailVerificationToken.objects.create(user=self.user)
        
        # Token yeni oluşturuldu, süresi dolmamış olmalı
        self.assertFalse(token.is_expired())
    
    def test_email_verification_token_is_expired_true(self):
        """EmailVerificationToken süresi dolmuş testi"""
        token = EmailVerificationToken.objects.create(user=self.user)
        
        # Token'ı 25 saat önce oluşturulmuş gibi yap (24 saatlik süre dolmuş)
        expired_time = timezone.now() - timedelta(hours=25)
        token.created_at = expired_time
        token.save()
        
        self.assertTrue(token.is_expired())
    
    def test_email_verification_token_is_expired_boundary(self):
        """EmailVerificationToken süre sınırı testi"""
        token = EmailVerificationToken.objects.create(user=self.user)
        
        # Token'ı 24 saat + 1 dakika önce oluşturulmuş gibi yap
        boundary_time = timezone.now() - timedelta(hours=24, minutes=1)
        token.created_at = boundary_time
        token.save()
        
        # 24 saatten sonra süre dolmuş sayılmalı
        self.assertTrue(token.is_expired())
    
    def test_email_verification_token_multiple_tokens_per_user(self):
        """Kullanıcı başına birden fazla token testi"""
        # Aynı kullanıcı için birden fazla token oluştur
        token1 = EmailVerificationToken.objects.create(user=self.user)
        token2 = EmailVerificationToken.objects.create(user=self.user)
        
        # Her iki token da oluşturulmuş olmalı
        self.assertEqual(EmailVerificationToken.objects.filter(user=self.user).count(), 2)
        
        # Token'lar farklı olmalı
        self.assertNotEqual(token1.token, token2.token)
    
    def test_email_verification_token_mark_as_used(self):
        """EmailVerificationToken kullanıldı olarak işaretleme testi"""
        token = EmailVerificationToken.objects.create(user=self.user)
        
        self.assertFalse(token.is_used)
        
        # Token'ı kullanıldı olarak işaretle
        token.is_used = True
        token.save()
        
        updated_token = EmailVerificationToken.objects.get(pk=token.pk)
        self.assertTrue(updated_token.is_used)
    
    def test_email_verification_token_cascade_delete(self):
        """EmailVerificationToken cascade delete testi"""
        token = EmailVerificationToken.objects.create(user=self.user)
        
        # Kullanıcıyı sil
        self.user.delete()
        
        # Token da silinmiş olmalı
        self.assertFalse(EmailVerificationToken.objects.filter(pk=token.pk).exists())


class TestOrganisorModel(TestCase):
    """Organisor modeli testleri"""
    
    def setUp(self):
        """Test verilerini hazırla"""
        # Bu test class'ında setUp'da user oluşturmayalım
        # Her test kendi user'ını oluşturacak
        pass
    
    def test_organisor_creation(self):
        """Organisor oluşturma testi"""
        # Test için yeni bir user oluştur
        test_user = User.objects.create_user(
            username='testuser_organisor_creation',
            email='test_organisor_creation@example.com',
            password='testpass123!',
            is_organisor=True
        )
        # Signal nedeniyle UserProfile zaten oluşturulmuş olmalı
        test_user_profile = UserProfile.objects.get(user=test_user)
        
        organisor = Organisor.objects.create(
            user=test_user,
            organisation=test_user_profile
        )
        
        self.assertEqual(organisor.user, test_user)
        self.assertEqual(organisor.organisation, test_user_profile)
        self.assertEqual(str(organisor), 'test_organisor_creation@example.com')
    
    def test_organisor_str_method(self):
        """Organisor __str__ metodu testi"""
        # Test için yeni bir user oluştur
        test_user = User.objects.create_user(
            username='testuser_organisor_str',
            email='test_organisor_str@example.com',
            password='testpass123!',
            is_organisor=True
        )
        # Signal nedeniyle UserProfile zaten oluşturulmuş olmalı
        test_user_profile = UserProfile.objects.get(user=test_user)
        
        organisor = Organisor.objects.create(
            user=test_user,
            organisation=test_user_profile
        )
        
        self.assertEqual(str(organisor), 'test_organisor_str@example.com')
    
    def test_organisor_cascade_delete(self):
        """Organisor cascade delete testi"""
        # Test için yeni bir user oluştur
        test_user = User.objects.create_user(
            username='testuser_organisor_cascade',
            email='test_organisor_cascade@example.com',
            password='testpass123!',
            is_organisor=True
        )
        # Signal nedeniyle UserProfile zaten oluşturulmuş olmalı
        test_user_profile = UserProfile.objects.get(user=test_user)
        
        organisor = Organisor.objects.create(
            user=test_user,
            organisation=test_user_profile
        )
        
        # Kullanıcıyı sil
        test_user.delete()
        
        # Organisor da silinmiş olmalı
        self.assertFalse(Organisor.objects.filter(pk=organisor.pk).exists())


class TestSignupModelIntegration(TestCase):
    """Signup model entegrasyon testleri"""
    
    def setUp(self):
        """Test verilerini hazırla"""
        self.user_data = {
            'username': 'integration_test_user',
            'email': 'integration_test@example.com',
            'password': 'testpass123!',
            'first_name': 'Integration',
            'last_name': 'Test',
            'phone_number': '+905559876543',
            'date_of_birth': datetime(1985, 5, 15).date(),
            'gender': 'F',
            'is_organisor': True,
            'email_verified': False,
        }
    
    def test_complete_signup_model_creation(self):
        """Tam signup model oluşturma testi"""
        # Test için benzersiz user data oluştur
        user_data = self.user_data.copy()
        user_data['username'] = 'integration_test_user_complete'
        user_data['email'] = 'integration_test_complete@example.com'
        
        # 1. User oluştur
        user = User.objects.create_user(**user_data)
        
        # 2. UserProfile zaten signal ile oluşturulmuş olmalı
        user_profile = UserProfile.objects.get(user=user)
        
        # 3. Organisor oluştur
        organisor = Organisor.objects.create(
            user=user,
            organisation=user_profile
        )
        
        # 4. EmailVerificationToken oluştur
        verification_token = EmailVerificationToken.objects.create(user=user)
        
        # Tüm modeller doğru oluşturuldu mu
        self.assertEqual(User.objects.filter(username='integration_test_user_complete').count(), 1)
        self.assertEqual(UserProfile.objects.filter(user=user).count(), 1)
        self.assertEqual(Organisor.objects.filter(user=user).count(), 1)
        self.assertEqual(EmailVerificationToken.objects.filter(user=user).count(), 1)
        
        # İlişkiler doğru mu
        self.assertEqual(organisor.user, user)
        self.assertEqual(organisor.organisation, user_profile)
        self.assertEqual(verification_token.user, user)
    
    def test_signup_model_relationships(self):
        """Signup model ilişkileri testi"""
        # Test için benzersiz user data oluştur
        user_data = self.user_data.copy()
        user_data['username'] = 'integration_test_user_relationships'
        user_data['email'] = 'integration_test_relationships@example.com'
        
        # Tam signup süreci
        user = User.objects.create_user(**user_data)
        user_profile = UserProfile.objects.get(user=user)
        organisor = Organisor.objects.create(user=user, organisation=user_profile)
        verification_token = EmailVerificationToken.objects.create(user=user)
        
        # User'dan diğer modellere erişim
        self.assertEqual(user.userprofile, user_profile)
        self.assertEqual(user.organisor, organisor)
        self.assertTrue(EmailVerificationToken.objects.filter(user=user).exists())
        
        # UserProfile'dan User'a erişim
        self.assertEqual(user_profile.user, user)
        
        # Organisor'dan User ve UserProfile'a erişim
        self.assertEqual(organisor.user, user)
        self.assertEqual(organisor.organisation, user_profile)
        
        # EmailVerificationToken'dan User'a erişim
        self.assertEqual(verification_token.user, user)
    
    def test_signup_model_cascade_operations(self):
        """Signup model cascade işlemleri testi"""
        # Test için benzersiz user data oluştur
        user_data = self.user_data.copy()
        user_data['username'] = 'integration_test_user_cascade'
        user_data['email'] = 'integration_test_cascade@example.com'
        
        # Tam signup süreci
        user = User.objects.create_user(**user_data)
        user_profile = UserProfile.objects.get(user=user)
        organisor = Organisor.objects.create(user=user, organisation=user_profile)
        verification_token = EmailVerificationToken.objects.create(user=user)
        
        user_pk = user.pk
        user_profile_pk = user_profile.pk
        organisor_pk = organisor.pk
        verification_token_pk = verification_token.pk
        
        # User'ı sil
        user.delete()
        
        # Tüm ilişkili modeller silinmiş olmalı
        self.assertFalse(User.objects.filter(pk=user_pk).exists())
        self.assertFalse(UserProfile.objects.filter(pk=user_profile_pk).exists())
        self.assertFalse(Organisor.objects.filter(pk=organisor_pk).exists())
        self.assertFalse(EmailVerificationToken.objects.filter(pk=verification_token_pk).exists())
    
    def test_signup_model_data_integrity(self):
        """Signup model veri bütünlüğü testi"""
        # Test için benzersiz user data oluştur
        user_data = self.user_data.copy()
        user_data['username'] = 'integration_test_user_data_consistency'
        user_data['email'] = 'integration_test_data_consistency@example.com'
        
        # Tam signup süreci
        user = User.objects.create_user(**user_data)
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
    
    def test_signup_model_validation(self):
        """Signup model validasyon testi"""
        # Model validation testleri
        
        # Boş username - Django bunu kabul etmiyor
        with self.assertRaises(ValueError):
            User.objects.create_user(
                username='',
                email='test@example.com',
                password='testpass123!'
            )
        
        # Model validation'ın çalıştığını test et
        user = User.objects.create_user(
            username='validation_test_user',
            email='validation@example.com',
            password='testpass123!'
        )
        
        # User başarıyla oluşturuldu
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'validation_test_user')
        
        # Boş kullanıcı adı
        with self.assertRaises(Exception):
            User.objects.create_user(
                username='',
                email='test@example.com',
                password='testpass123!'
            )


if __name__ == "__main__":
    print("Signup Model Testleri Başlatılıyor...")
    print("=" * 60)
    
    # Test çalıştırma
    import unittest
    unittest.main()
