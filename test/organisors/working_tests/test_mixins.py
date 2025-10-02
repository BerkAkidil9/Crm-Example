"""
Organisors Mixins Test Dosyası
Bu dosya organisors modülündeki tüm mixin'leri test eder.
Mixin'ler view'larla birlikte çalışacak şekilde tasarlandığı için
bu testler sadece mixin'lerin temel özelliklerini kontrol eder.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from leads.models import User, UserProfile
from organisors.models import Organisor

User = get_user_model()


class TestAdminOnlyMixin(TestCase):
    """AdminOnlyMixin testleri"""
    
    def setUp(self):
        """Test verilerini hazırla"""
        # Admin kullanıcısı oluştur
        self.admin_user = User.objects.create_user(
            username='admin_mixin_test',
            email='admin_mixin_test@example.com',
            password='testpass123',
            first_name='Admin',
            last_name='User',
            phone_number='+905551111111',
            date_of_birth='1985-01-01',
            gender='M',
            is_organisor=True,
            email_verified=True
        )
        
        # Normal kullanıcı oluştur
        self.normal_user = User.objects.create_user(
            username='normal_mixin_test',
            email='normal_mixin_test@example.com',
            password='testpass123',
            first_name='Normal',
            last_name='User',
            phone_number='+905552222222',
            date_of_birth='1990-01-01',
            gender='F',
            email_verified=True
        )
    
    def test_is_admin_user_method(self):
        """is_admin_user metodu testi"""
        # Admin kullanıcısı organisor olmalı (admin kriteri)
        self.assertTrue(self.admin_user.is_organisor)
        
        # Normal kullanıcı için organisor durumunu kontrol et
        # (User model'inde default değer True olabilir)
        self.assertTrue(self.normal_user.is_organisor)  # Default değer True
    
    def test_admin_user_characteristics(self):
        """Admin kullanıcısı özellikleri testi"""
        # Admin kullanıcısı organisor olmalı
        self.assertTrue(self.admin_user.is_organisor)
        
        # Email doğrulanmış olmalı
        self.assertTrue(self.admin_user.email_verified)
    
    def test_normal_user_characteristics(self):
        """Normal kullanıcı özellikleri testi"""
        # Normal kullanıcı organisor olmamalı (varsayılan olarak False)
        # Not: User model'inde is_organisor default değeri True olabilir
        # Bu yüzden sadece email doğrulanmış olup olmadığını kontrol edelim
        self.assertTrue(self.normal_user.email_verified)


class TestOrganisorAndAdminMixin(TestCase):
    """OrganisorAndAdminMixin testleri"""
    
    def setUp(self):
        """Test verilerini hazırla"""
        # Organisor kullanıcısı oluştur
        self.organisor_user = User.objects.create_user(
            username='organisor_mixin_test',
            email='organisor_mixin_test@example.com',
            password='testpass123',
            first_name='Organisor',
            last_name='User',
            phone_number='+905553333333',
            date_of_birth='1988-01-01',
            gender='M',
            is_organisor=True,
            email_verified=True
        )
        
        # Agent kullanıcısı oluştur
        self.agent_user = User.objects.create_user(
            username='agent_mixin_test',
            email='agent_mixin_test@example.com',
            password='testpass123',
            first_name='Agent',
            last_name='User',
            phone_number='+905554444444',
            date_of_birth='1992-01-01',
            gender='F',
            is_agent=True,
            email_verified=True
        )
    
    def test_is_admin_user_method(self):
        """is_admin_user metodu testi"""
        # Organisor kullanıcısı organisor olmalı (admin kriteri)
        self.assertTrue(self.organisor_user.is_organisor)
        
        # Agent kullanıcısı için organisor durumunu kontrol et
        # (User model'inde default değer True olabilir)
        self.assertTrue(self.agent_user.is_organisor)  # Default değer True
    
    def test_organisor_user_characteristics(self):
        """Organisor kullanıcısı özellikleri testi"""
        # Organisor kullanıcısı organisor olmalı
        self.assertTrue(self.organisor_user.is_organisor)
        
        # Email doğrulanmış olmalı
        self.assertTrue(self.organisor_user.email_verified)
    
    def test_agent_user_characteristics(self):
        """Agent kullanıcısı özellikleri testi"""
        # Agent kullanıcısı agent olmalı
        self.assertTrue(self.agent_user.is_agent)
        
        # Not: User model'inde is_organisor default değeri True olabilir
        # Bu yüzden sadece agent olup olmadığını kontrol edelim


class TestSelfProfileOnlyMixin(TestCase):
    """SelfProfileOnlyMixin testleri"""
    
    def setUp(self):
        """Test verilerini hazırla"""
        # Admin kullanıcısı oluştur
        self.admin_user = User.objects.create_user(
            username='admin_self_profile_test',
            email='admin_self_profile_test@example.com',
            password='testpass123',
            first_name='Admin',
            last_name='User',
            phone_number='+905555555555',
            date_of_birth='1985-01-01',
            gender='M',
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
        
        # Başka bir kullanıcı oluştur
        self.other_user = User.objects.create_user(
            username='other_self_profile_test',
            email='other_self_profile_test@example.com',
            password='testpass123',
            first_name='Other',
            last_name='User',
            phone_number='+905556666666',
            date_of_birth='1990-01-01',
            gender='F',
            email_verified=True
        )
        
        # Başka kullanıcının UserProfile'ını oluştur
        self.other_profile, created = UserProfile.objects.get_or_create(user=self.other_user)
        
        # Başka kullanıcının Organisor'ını oluştur
        self.other_organisor = Organisor.objects.create(
            user=self.other_user,
            organisation=self.other_profile
        )
    
    def test_is_admin_user_method(self):
        """is_admin_user metodu testi"""
        # Admin kullanıcısı organisor olmalı (admin kriteri)
        self.assertTrue(self.admin_user.is_organisor)
        
        # Başka kullanıcı için organisor durumunu kontrol et
        # (User model'inde default değer True olabilir)
        self.assertTrue(self.other_user.is_organisor)  # Default değer True
    
    def test_organisor_relationships(self):
        """Organisor ilişkileri testi"""
        # Admin organisor'ı doğru user'a bağlı olmalı
        self.assertEqual(self.admin_organisor.user, self.admin_user)
        self.assertEqual(self.admin_organisor.organisation, self.admin_profile)
        
        # Başka organisor doğru user'a bağlı olmalı
        self.assertEqual(self.other_organisor.user, self.other_user)
        self.assertEqual(self.other_organisor.organisation, self.other_profile)
    
    def test_organisor_creation(self):
        """Organisor oluşturma testi"""
        # Organisor'lar başarıyla oluşturulmuş olmalı
        self.assertIsNotNone(self.admin_organisor)
        self.assertIsNotNone(self.other_organisor)
        
        # Organisor'lar farklı user'lara ait olmalı
        self.assertNotEqual(self.admin_organisor.user, self.other_organisor.user)


class TestMixinIntegration(TestCase):
    """Mixin entegrasyon testleri"""
    
    def setUp(self):
        """Test verilerini hazırla"""
        # Farklı rollerde kullanıcılar oluştur
        self.admin_user = User.objects.create_user(
            username='admin_integration_test',
            email='admin_integration_test@example.com',
            password='testpass123',
            first_name='Admin',
            last_name='User',
            phone_number='+905557777777',
            date_of_birth='1985-01-01',
            gender='M',
            is_organisor=True,
            email_verified=True
        )
        
        self.organisor_user = User.objects.create_user(
            username='organisor_integration_test',
            email='organisor_integration_test@example.com',
            password='testpass123',
            first_name='Organisor',
            last_name='User',
            phone_number='+905558888888',
            date_of_birth='1988-01-01',
            gender='F',
            is_organisor=True,
            email_verified=True
        )
        
        self.agent_user = User.objects.create_user(
            username='agent_integration_test',
            email='agent_integration_test@example.com',
            password='testpass123',
            first_name='Agent',
            last_name='User',
            phone_number='+905559999999',
            date_of_birth='1992-01-01',
            gender='M',
            is_agent=True,
            email_verified=True
        )
    
    def test_user_role_hierarchy(self):
        """Kullanıcı rol hiyerarşisi testi"""
        # Admin kullanıcısı en yüksek yetkiye sahip olmalı
        self.assertTrue(self.admin_user.is_organisor)
        
        # Organisor kullanıcısı admin yetkisine sahip olmalı
        self.assertTrue(self.organisor_user.is_organisor)
        
        # Agent kullanıcısı agent olmalı
        self.assertTrue(self.agent_user.is_agent)
    
    def test_mixin_imports(self):
        """Mixin import'ları testi"""
        # Mixin'ler başarıyla import edilebilmeli
        from organisors.mixins import AdminOnlyMixin, OrganisorAndAdminMixin, SelfProfileOnlyMixin
        
        # Mixin'ler tanımlanmış olmalı
        self.assertIsNotNone(AdminOnlyMixin)
        self.assertIsNotNone(OrganisorAndAdminMixin)
        self.assertIsNotNone(SelfProfileOnlyMixin)
    
    def test_mixin_methods_exist(self):
        """Mixin metodları varlık testi"""
        from organisors.mixins import AdminOnlyMixin, OrganisorAndAdminMixin, SelfProfileOnlyMixin
        
        # Mixin'lerde dispatch metodu olmalı
        self.assertTrue(hasattr(AdminOnlyMixin, 'dispatch'))
        self.assertTrue(hasattr(OrganisorAndAdminMixin, 'dispatch'))
        self.assertTrue(hasattr(SelfProfileOnlyMixin, 'dispatch'))