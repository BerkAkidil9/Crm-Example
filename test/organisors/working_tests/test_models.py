"""
Organisors Modelleri Test Dosyası
Bu dosya organisors modülündeki tüm modelleri test eder.
"""

import os
import sys
import django
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djcrm.settings')
django.setup()

from organisors.models import Organisor
from leads.models import User, UserProfile


class TestOrganisorModel(TestCase):
    """Organisor modeli testleri"""
    
    def setUp(self):
        """Test verilerini hazırla"""
        # Test kullanıcısı oluştur
        self.user = User.objects.create_user(
            username="testuser_organisor_models",
            email="test_organisor_models@example.com",
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
    
    def test_organisor_creation(self):
        """Organisor oluşturma testi"""
        self.assertEqual(self.organisor.user, self.user)
        self.assertEqual(self.organisor.organisation, self.user_profile)
        self.assertIsNotNone(self.organisor)
    
    def test_organisor_str_representation(self):
        """Organisor __str__ metodu testi"""
        self.assertEqual(str(self.organisor), self.user.email)
    
    def test_organisor_verbose_names(self):
        """Organisor verbose name testleri"""
        self.assertEqual(Organisor._meta.verbose_name, "Organisor")
        self.assertEqual(Organisor._meta.verbose_name_plural, "Organisors")
    
    def test_organisor_user_relationship(self):
        """Organisor-User ilişkisi testi"""
        self.assertEqual(self.organisor.user, self.user)
        self.assertTrue(hasattr(self.user, 'organisor'))
        self.assertEqual(self.user.organisor, self.organisor)
    
    def test_organisor_organisation_relationship(self):
        """Organisor-Organisation ilişkisi testi"""
        self.assertEqual(self.organisor.organisation, self.user_profile)
        self.assertIn(self.organisor, self.user_profile.organisor_set.all())
    
    def test_organisor_user_one_to_one(self):
        """Organisor-User OneToOneField testi"""
        # Aynı kullanıcı için ikinci bir organisor oluşturulamaz
        with self.assertRaises(IntegrityError):
            Organisor.objects.create(
                user=self.user,
                organisation=self.user_profile
            )
    
    def test_organisor_cascade_delete_user(self):
        """User silinince Organisor da silinir testi"""
        user_id = self.user.id
        organisor_id = self.organisor.id
        
        # User'ı sil
        self.user.delete()
        
        # Organisor da silinmiş olmalı
        self.assertFalse(Organisor.objects.filter(id=organisor_id).exists())
        self.assertFalse(User.objects.filter(id=user_id).exists())
    
    def test_organisor_cascade_delete_organisation(self):
        """Organisation silinince Organisor da silinir testi"""
        # Yeni bir organisor oluştur
        user2 = User.objects.create_user(
            username="testuser2_organisor_models",
            email="test2_organisor_models@example.com",
            password="testpass123",
            is_organisor=True
        )
        user_profile2, created = UserProfile.objects.get_or_create(user=user2)
        organisor2 = Organisor.objects.create(
            user=user2,
            organisation=user_profile2
        )
        
        organisor_id = organisor2.id
        user_profile_id = user_profile2.id
        
        # UserProfile'ı sil
        user_profile2.delete()
        
        # Organisor da silinmiş olmalı
        self.assertFalse(Organisor.objects.filter(id=organisor_id).exists())
        self.assertFalse(UserProfile.objects.filter(id=user_profile_id).exists())
    
    def test_organisor_multiple_organisations(self):
        """Bir kullanıcının birden fazla organisor kaydı olamaz testi"""
        # Aynı kullanıcı için farklı organisation ile organisor oluşturulamaz
        user2 = User.objects.create_user(
            username="testuser3_organisor_models",
            email="test3_organisor_models@example.com",
            password="testpass123",
            is_organisor=True
        )
        user_profile2, created = UserProfile.objects.get_or_create(user=user2)
        
        # Aynı user ile ikinci organisor oluşturulamaz
        with self.assertRaises(IntegrityError):
            Organisor.objects.create(
                user=self.user,  # Aynı user
                organisation=user_profile2  # Farklı organisation
            )
    
    def test_organisor_model_fields(self):
        """Organisor model alanları testi"""
        # Model alanlarının varlığını kontrol et
        self.assertTrue(hasattr(self.organisor, 'user'))
        self.assertTrue(hasattr(self.organisor, 'organisation'))
        self.assertTrue(hasattr(self.organisor, 'id'))
    
    def test_organisor_foreign_key_constraints(self):
        """Organisor foreign key kısıtlamaları testi"""
        # Bu test Django'nun built-in constraint'lerini test eder
        # Foreign key alanları required olduğu için None değerler kabul edilmez
        # Bu durum Django ORM seviyesinde değil, veritabanı seviyesinde kontrol edilir
        
        # Organisor modeli doğru foreign key alanlarına sahip mi?
        self.assertTrue(hasattr(Organisor._meta.get_field('user'), 'null'))
        self.assertTrue(hasattr(Organisor._meta.get_field('organisation'), 'null'))
        
        # Foreign key alanları null=False olmalı
        self.assertFalse(Organisor._meta.get_field('user').null)
        self.assertFalse(Organisor._meta.get_field('organisation').null)


class TestOrganisorModelRelationships(TestCase):
    """Organisor model ilişkileri testleri"""
    
    def setUp(self):
        """Test verilerini hazırla"""
        # Admin kullanıcısı oluştur
        self.admin_user = User.objects.create_user(
            username="admin_organisor_relationships",
            email="admin_organisor_relationships@example.com",
            password="testpass123",
            first_name="Admin",
            last_name="User",
            phone_number="+905551111111",
            date_of_birth="1985-01-01",
            gender="M",
            is_organisor=True,
            email_verified=True
        )
        
        # Admin UserProfile oluştur
        self.admin_profile, created = UserProfile.objects.get_or_create(user=self.admin_user)
        
        # Admin Organisor oluştur
        self.admin_organisor = Organisor.objects.create(
            user=self.admin_user,
            organisation=self.admin_profile
        )
        
        # Normal kullanıcı oluştur
        self.normal_user = User.objects.create_user(
            username="normal_organisor_relationships",
            email="normal_organisor_relationships@example.com",
            password="testpass123",
            first_name="Normal",
            last_name="User",
            phone_number="+905552222222",
            date_of_birth="1990-01-01",
            gender="F",
            is_organisor=True,
            email_verified=True
        )
        
        # Normal UserProfile oluştur
        self.normal_profile, created = UserProfile.objects.get_or_create(user=self.normal_user)
        
        # Normal Organisor oluştur
        self.normal_organisor = Organisor.objects.create(
            user=self.normal_user,
            organisation=self.admin_profile  # Admin'in organisation'ına bağlı
        )
    
    def test_organisor_organisation_hierarchy(self):
        """Organisor organisation hiyerarşisi testi"""
        # Normal organisor, admin'in organisation'ına bağlı
        self.assertEqual(self.normal_organisor.organisation, self.admin_profile)
        self.assertNotEqual(self.normal_organisor.organisation, self.normal_profile)
    
    def test_organisor_user_profile_consistency(self):
        """Organisor user profile tutarlılığı testi"""
        # Her organisor'ın kendi user'ı var
        self.assertEqual(self.admin_organisor.user, self.admin_user)
        self.assertEqual(self.normal_organisor.user, self.normal_user)
        
        # User'ların organisor kayıtları var
        self.assertEqual(self.admin_user.organisor, self.admin_organisor)
        self.assertEqual(self.normal_user.organisor, self.normal_organisor)
    
    def test_organisor_organisation_access(self):
        """Organisor organisation erişimi testi"""
        # Admin'in organisation'ına bağlı organisorlar
        admin_organisors = Organisor.objects.filter(organisation=self.admin_profile)
        self.assertIn(self.admin_organisor, admin_organisors)
        self.assertIn(self.normal_organisor, admin_organisors)
        self.assertEqual(admin_organisors.count(), 2)
    
    def test_organisor_user_queries(self):
        """Organisor user sorguları testi"""
        # Organisor'dan user'a erişim
        self.assertEqual(self.admin_organisor.user.username, "admin_organisor_relationships")
        self.assertEqual(self.normal_organisor.user.email, "normal_organisor_relationships@example.com")
        
        # User'dan organisor'a erişim
        self.assertEqual(self.admin_user.organisor.organisation, self.admin_profile)
        self.assertEqual(self.normal_user.organisor.organisation, self.admin_profile)
    
    def test_organisor_organisation_queries(self):
        """Organisor organisation sorguları testi"""
        # Organisation'dan organisor'lara erişim
        organisors = self.admin_profile.organisor_set.all()
        self.assertEqual(organisors.count(), 2)
        self.assertIn(self.admin_organisor, organisors)
        self.assertIn(self.normal_organisor, organisors)
        
        # Organisor'dan organisation'a erişim
        self.assertEqual(self.admin_organisor.organisation.user, self.admin_user)
        self.assertEqual(self.normal_organisor.organisation.user, self.admin_user)


class TestOrganisorModelEdgeCases(TestCase):
    """Organisor model sınır durumları testleri"""
    
    def test_organisor_with_deleted_user(self):
        """Silinmiş user ile organisor testi"""
        # User oluştur
        user = User.objects.create_user(
            username="deleted_user_organisor",
            email="deleted_user_organisor@example.com",
            password="testpass123",
            is_organisor=True
        )
        
        # UserProfile oluştur
        user_profile, created = UserProfile.objects.get_or_create(user=user)
        
        # Organisor oluştur
        organisor = Organisor.objects.create(
            user=user,
            organisation=user_profile
        )
        
        # User'ı sil
        user.delete()
        
        # Organisor da silinmiş olmalı
        self.assertFalse(Organisor.objects.filter(id=organisor.id).exists())
    
    def test_organisor_with_deleted_organisation(self):
        """Silinmiş organisation ile organisor testi"""
        # User oluştur
        user = User.objects.create_user(
            username="deleted_org_organisor",
            email="deleted_org_organisor@example.com",
            password="testpass123",
            is_organisor=True
        )
        
        # UserProfile oluştur
        user_profile, created = UserProfile.objects.get_or_create(user=user)
        
        # Organisor oluştur
        organisor = Organisor.objects.create(
            user=user,
            organisation=user_profile
        )
        
        # UserProfile'ı sil
        user_profile.delete()
        
        # Organisor da silinmiş olmalı
        self.assertFalse(Organisor.objects.filter(id=organisor.id).exists())
    
    def test_organisor_model_meta_options(self):
        """Organisor model Meta seçenekleri testi"""
        # Model Meta seçeneklerini kontrol et
        meta = Organisor._meta
        self.assertEqual(meta.verbose_name, "Organisor")
        self.assertEqual(meta.verbose_name_plural, "Organisors")
        
        # Model alanlarını kontrol et
        field_names = [field.name for field in meta.fields]
        self.assertIn('id', field_names)
        self.assertIn('user', field_names)
        self.assertIn('organisation', field_names)
    
    def test_organisor_model_constraints(self):
        """Organisor model kısıtlamaları testi"""
        # OneToOneField kısıtlaması
        user = User.objects.create_user(
            username="constraint_test_user",
            email="constraint_test_user@example.com",
            password="testpass123",
            is_organisor=True
        )
        user_profile, created = UserProfile.objects.get_or_create(user=user)
        
        # İlk organisor oluştur
        Organisor.objects.create(
            user=user,
            organisation=user_profile
        )
        
        # Aynı user ile ikinci organisor oluşturulamaz
        with self.assertRaises(IntegrityError):
            Organisor.objects.create(
                user=user,
                organisation=user_profile
            )


if __name__ == "__main__":
    print("Organisors Modelleri Testleri Başlatılıyor...")
    print("=" * 60)
    
    # Test çalıştırma
    import unittest
    unittest.main()
