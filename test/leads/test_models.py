"""
Leads Models Test Dosyası
Bu dosya Leads modülündeki tüm modelleri test eder.
"""

import os
import sys
import django
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import IntegrityError
from unittest.mock import patch, MagicMock
from datetime import timedelta

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djcrm.settings')
django.setup()

from leads.models import User, UserProfile, Lead, Agent, EmailVerificationToken, Category, SourceCategory, ValueCategory
from organisors.models import Organisor

User = get_user_model()


class TestUserModel(TestCase):
    """User model testleri"""
    
    def setUp(self):
        """Set up test data"""
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'phone_number': '+905551234567',
            'date_of_birth': '1990-01-01',
            'gender': 'M',
            'is_organisor': True,
            'is_agent': False,
            'email_verified': True
        }
    
    def test_user_creation(self):
        """User oluşturma testi"""
        user = User.objects.create_user(**self.user_data)
        
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User')
        self.assertEqual(user.phone_number, '+905551234567')
        self.assertEqual(user.date_of_birth, '1990-01-01')
        self.assertEqual(user.gender, 'M')
        self.assertTrue(user.is_organisor)
        self.assertFalse(user.is_agent)
        self.assertTrue(user.email_verified)
    
    def test_user_str_representation(self):
        """User __str__ metodu testi"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(str(user), 'testuser')
    
    def test_user_email_unique(self):
        """User email benzersizlik testi"""
        User.objects.create_user(**self.user_data)
        
        # Aynı email ile ikinci user oluşturmaya çalış
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username='testuser2',
                email='test@example.com',
                password='testpass123'
            )
    
    def test_user_username_unique(self):
        """User username benzersizlik testi"""
        User.objects.create_user(**self.user_data)
        
        # Aynı username ile ikinci user oluşturmaya çalış
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username='testuser',
                email='test2@example.com',
                password='testpass123'
            )
    
    def test_user_phone_number_unique(self):
        """User phone_number benzersizlik testi"""
        User.objects.create_user(**self.user_data)
        
        # Aynı phone_number ile ikinci user oluşturmaya çalış
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username='testuser2',
                email='test2@example.com',
                password='testpass123',
                phone_number='+905551234567'
            )
    
    def test_user_gender_choices(self):
        """User gender seçenekleri testi"""
        # Geçerli gender değerleri
        valid_genders = ['M', 'F', 'O']
        for i, gender in enumerate(valid_genders):
            user_data = self.user_data.copy()
            user_data['username'] = f'testuser_{gender}_{i}'
            user_data['email'] = f'test_{gender}_{i}@example.com'
            user_data['phone_number'] = f'+90555123456{i}'
            user_data['gender'] = gender
            
            user = User.objects.create_user(**user_data)
            self.assertEqual(user.gender, gender)
    
    def test_user_default_values(self):
        """User default değerleri testi"""
        user = User.objects.create_user(
            username='defaultuser',
            email='default@example.com',
            password='testpass123'
        )
        
        self.assertTrue(user.is_organisor)  # Default True
        self.assertFalse(user.is_agent)    # Default False
        self.assertFalse(user.email_verified)  # Default False
        self.assertIsNone(user.phone_number)   # Default None
        self.assertIsNone(user.date_of_birth)  # Default None
        self.assertIsNone(user.gender)         # Default None


class TestUserProfileModel(TestCase):
    """UserProfile model testleri"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='profileuser',
            email='profile@example.com',
            password='testpass123',
            first_name='Profile',
            last_name='User',
            phone_number='+905551234567',
            date_of_birth='1990-01-01',
            gender='M',
            is_organisor=True,
            email_verified=True
        )
    
    def test_userprofile_creation(self):
        """UserProfile oluşturma testi"""
        # User oluşturulduğunda UserProfile otomatik oluşturulmuş olmalı
        self.assertTrue(UserProfile.objects.filter(user=self.user).exists())
        
        profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(profile.user, self.user)
        self.assertEqual(str(profile), 'profileuser')
    
    def test_userprofile_one_to_one_relationship(self):
        """UserProfile-OneToOneField ilişkisi testi"""
        # User oluşturulduğunda UserProfile otomatik oluşturulmuş olmalı
        profile = UserProfile.objects.get(user=self.user)
        
        # User'dan profile'a erişim
        self.assertEqual(self.user.userprofile, profile)
        
        # Profile'dan user'a erişim
        self.assertEqual(profile.user, self.user)
    
    def test_userprofile_unique_constraint(self):
        """UserProfile unique constraint testi"""
        # UserProfile zaten mevcut, yeni user ile test et
        new_user = User.objects.create_user(
            username='newuser',
            email='newuser@example.com',
            password='testpass123',
            phone_number='+905551234568'
        )
        
        # Aynı user ile ikinci profile oluşturmaya çalış
        with self.assertRaises(IntegrityError):
            UserProfile.objects.create(user=new_user)
    
    def test_userprofile_cascade_delete_user(self):
        """UserProfile cascade delete user testi"""
        profile = UserProfile.objects.get(user=self.user)
        profile_id = profile.id
        
        # User'ı sil
        self.user.delete()
        
        # Profile da silinmeli
        self.assertFalse(UserProfile.objects.filter(id=profile_id).exists())


class TestLeadModel(TestCase):
    """Lead model testleri"""
    
    def setUp(self):
        """Set up test data"""
        # Organisor kullanıcısı oluştur
        self.organisor_user = User.objects.create_user(
            username='lead_organisor_test',
            email='lead_organisor_test@example.com',
            password='testpass123',
            first_name='Lead',
            last_name='Organisor',
            phone_number='+905551234567',
            date_of_birth='1980-01-01',
            gender='M',
            is_organisor=True,
            email_verified=True
        )
        
        # UserProfile oluştur
        self.organisor_profile, created = UserProfile.objects.get_or_create(
            user=self.organisor_user
        )
        
        # Agent oluştur
        self.agent_user = User.objects.create_user(
            username='lead_agent_test',
            email='lead_agent_test@example.com',
            password='testpass123',
            first_name='Lead',
            last_name='Agent',
            phone_number='+905559876543',
            date_of_birth='1990-01-01',
            gender='F',
            is_agent=True,
            email_verified=True
        )
        
        self.agent_profile, created = UserProfile.objects.get_or_create(
            user=self.agent_user
        )
        
        self.agent = Agent.objects.create(
            user=self.agent_user,
            organisation=self.organisor_profile
        )
        
        # Kategoriler oluştur
        self.category = Category.objects.create(
            name="Test Category",
            organisation=self.organisor_profile
        )
        
        self.source_category = SourceCategory.objects.create(
            name="Website",
            organisation=self.organisor_profile
        )
        
        self.value_category = ValueCategory.objects.create(
            name="High Value",
            organisation=self.organisor_profile
        )
    
    def test_lead_creation(self):
        """Lead oluşturma testi"""
        lead = Lead.objects.create(
            first_name='John',
            last_name='Doe',
            age=30,
            organisation=self.organisor_profile,
            agent=self.agent,
            category=self.category,
            source_category=self.source_category,
            value_category=self.value_category,
            description='Test lead description',
            phone_number='+905551111111',
            email='john.doe@example.com',
            address='123 Test Street'
        )
        
        self.assertEqual(lead.first_name, 'John')
        self.assertEqual(lead.last_name, 'Doe')
        self.assertEqual(lead.age, 30)
        self.assertEqual(lead.organisation, self.organisor_profile)
        self.assertEqual(lead.agent, self.agent)
        self.assertEqual(lead.category, self.category)
        self.assertEqual(lead.source_category, self.source_category)
        self.assertEqual(lead.value_category, self.value_category)
        self.assertEqual(lead.description, 'Test lead description')
        self.assertEqual(lead.phone_number, '+905551111111')
        self.assertEqual(lead.email, 'john.doe@example.com')
        self.assertEqual(lead.address, '123 Test Street')
        self.assertIsNotNone(lead.date_added)
    
    def test_lead_str_representation(self):
        """Lead __str__ metodu testi"""
        lead = Lead.objects.create(
            first_name='Jane',
            last_name='Smith',
            age=25,
            organisation=self.organisor_profile,
            description='Test lead',
            phone_number='+905552222222',
            email='jane.smith@example.com',
            address='456 Test Avenue'
        )
        
        self.assertEqual(str(lead), 'Jane Smith')
    
    def test_lead_email_unique(self):
        """Lead email benzersizlik testi"""
        Lead.objects.create(
            first_name='John',
            last_name='Doe',
            age=30,
            organisation=self.organisor_profile,
            description='Test lead',
            phone_number='+905551111111',
            email='john.doe@example.com',
            address='123 Test Street'
        )
        
        # Aynı email ile ikinci lead oluşturmaya çalış
        with self.assertRaises(IntegrityError):
            Lead.objects.create(
                first_name='Jane',
                last_name='Smith',
                age=25,
                organisation=self.organisor_profile,
                description='Test lead 2',
                phone_number='+905552222222',
                email='john.doe@example.com',
                address='456 Test Avenue'
            )
    
    def test_lead_phone_number_unique(self):
        """Lead phone_number benzersizlik testi"""
        Lead.objects.create(
            first_name='John',
            last_name='Doe',
            age=30,
            organisation=self.organisor_profile,
            description='Test lead',
            phone_number='+905551111111',
            email='john.doe@example.com',
            address='123 Test Street'
        )
        
        # Aynı phone_number ile ikinci lead oluşturmaya çalış
        with self.assertRaises(IntegrityError):
            Lead.objects.create(
                first_name='Jane',
                last_name='Smith',
                age=25,
                organisation=self.organisor_profile,
                description='Test lead 2',
                phone_number='+905551111111',
                email='jane.smith@example.com',
                address='456 Test Avenue'
            )
    
    def test_lead_organisation_relationship(self):
        """Lead-organisation ilişkisi testi"""
        lead = Lead.objects.create(
            first_name='John',
            last_name='Doe',
            age=30,
            organisation=self.organisor_profile,
            description='Test lead',
            phone_number='+905551111111',
            email='john.doe@example.com',
            address='123 Test Street'
        )
        
        self.assertEqual(lead.organisation, self.organisor_profile)
        self.assertEqual(lead.organisation.user, self.organisor_user)
    
    def test_lead_agent_relationship(self):
        """Lead-agent ilişkisi testi"""
        lead = Lead.objects.create(
            first_name='John',
            last_name='Doe',
            age=30,
            organisation=self.organisor_profile,
            agent=self.agent,
            description='Test lead',
            phone_number='+905551111111',
            email='john.doe@example.com',
            address='123 Test Street'
        )
        
        self.assertEqual(lead.agent, self.agent)
        self.assertEqual(lead.agent.user, self.agent_user)
    
    def test_lead_cascade_delete_organisation(self):
        """Lead cascade delete organisation testi"""
        lead = Lead.objects.create(
            first_name='John',
            last_name='Doe',
            age=30,
            organisation=self.organisor_profile,
            description='Test lead',
            phone_number='+905551111111',
            email='john.doe@example.com',
            address='123 Test Street'
        )
        
        lead_id = lead.id
        
        # Organisation'ı sil
        self.organisor_profile.delete()
        
        # Lead da silinmeli
        self.assertFalse(Lead.objects.filter(id=lead_id).exists())
    
    def test_lead_agent_set_null_on_delete(self):
        """Lead agent SET_NULL on delete testi"""
        lead = Lead.objects.create(
            first_name='John',
            last_name='Doe',
            age=30,
            organisation=self.organisor_profile,
            agent=self.agent,
            description='Test lead',
            phone_number='+905551111111',
            email='john.doe@example.com',
            address='123 Test Street'
        )
        
        # Agent'ı sil
        self.agent.delete()
        
        # Lead'de agent null olmalı
        lead.refresh_from_db()
        self.assertIsNone(lead.agent)
    
    def test_lead_save_method_default_categories(self):
        """Lead save metodu default kategoriler testi"""
        # Yeni lead oluştur (kategoriler olmadan)
        lead = Lead(
            first_name='John',
            last_name='Doe',
            age=30,
            organisation=self.organisor_profile,
            description='Test lead',
            phone_number='+905551111111',
            email='john.doe@example.com',
            address='123 Test Street'
        )
        
        # Save öncesi kategoriler None
        self.assertIsNone(lead.category)
        self.assertIsNone(lead.source_category)
        self.assertIsNone(lead.value_category)
        
        # Save işlemi
        lead.save()
        
        # Save sonrası default kategoriler atanmış olmalı
        self.assertIsNotNone(lead.category)
        self.assertIsNotNone(lead.source_category)
        self.assertIsNotNone(lead.value_category)
        
        # "Unassigned" kategorileri oluşturulmuş olmalı
        self.assertEqual(lead.category.name, "Unassigned")
        self.assertEqual(lead.source_category.name, "Unassigned")
        self.assertEqual(lead.value_category.name, "Unassigned")
    
    def test_lead_save_method_existing_categories(self):
        """Lead save metodu mevcut kategoriler testi"""
        # Mevcut kategorilerle lead oluştur
        lead = Lead(
            first_name='John',
            last_name='Doe',
            age=30,
            organisation=self.organisor_profile,
            category=self.category,
            source_category=self.source_category,
            value_category=self.value_category,
            description='Test lead',
            phone_number='+905551111111',
            email='john.doe@example.com',
            address='123 Test Street'
        )
        
        lead.save()
        
        # Mevcut kategoriler korunmalı
        self.assertEqual(lead.category, self.category)
        self.assertEqual(lead.source_category, self.source_category)
        self.assertEqual(lead.value_category, self.value_category)


class TestAgentModel(TestCase):
    """Agent model testleri"""
    
    def setUp(self):
        """Set up test data"""
        # Organisor kullanıcısı oluştur
        self.organisor_user = User.objects.create_user(
            username='agent_organisor_test',
            email='agent_organisor_test@example.com',
            password='testpass123',
            first_name='Agent',
            last_name='Organisor',
            phone_number='+905551234567',
            date_of_birth='1980-01-01',
            gender='M',
            is_organisor=True,
            email_verified=True
        )
        
        # UserProfile oluştur
        self.organisor_profile, created = UserProfile.objects.get_or_create(
            user=self.organisor_user
        )
        
        # Agent kullanıcısı oluştur
        self.agent_user = User.objects.create_user(
            username='agent_test',
            email='agent_test@example.com',
            password='testpass123',
            first_name='Agent',
            last_name='Test',
            phone_number='+905559876543',
            date_of_birth='1990-01-01',
            gender='F',
            is_agent=True,
            email_verified=True
        )
        
        self.agent_profile, created = UserProfile.objects.get_or_create(
            user=self.agent_user
        )
    
    def test_agent_creation(self):
        """Agent oluşturma testi"""
        agent = Agent.objects.create(
            user=self.agent_user,
            organisation=self.organisor_profile
        )
        
        self.assertEqual(agent.user, self.agent_user)
        self.assertEqual(agent.organisation, self.organisor_profile)
        self.assertTrue(Agent.objects.filter(user=self.agent_user).exists())
    
    def test_agent_str_representation(self):
        """Agent __str__ metodu testi"""
        agent = Agent.objects.create(
            user=self.agent_user,
            organisation=self.organisor_profile
        )
        
        expected_str = self.agent_user.email
        self.assertEqual(str(agent), expected_str)
    
    def test_agent_user_relationship(self):
        """Agent-User ilişkisi testi"""
        agent = Agent.objects.create(
            user=self.agent_user,
            organisation=self.organisor_profile
        )
        
        # OneToOneField testi
        self.assertEqual(agent.user, self.agent_user)
        self.assertEqual(agent.user.is_agent, True)
        self.assertEqual(agent.user.is_organisor, True)
    
    def test_agent_organisation_relationship(self):
        """Agent-Organisation ilişkisi testi"""
        agent = Agent.objects.create(
            user=self.agent_user,
            organisation=self.organisor_profile
        )
        
        # ForeignKey testi
        self.assertEqual(agent.organisation, self.organisor_profile)
        self.assertEqual(agent.organisation.user, self.organisor_user)
    
    def test_agent_unique_user_constraint(self):
        """Agent unique user constraint testi"""
        # İlk agent oluştur
        Agent.objects.create(
            user=self.agent_user,
            organisation=self.organisor_profile
        )
        
        # Aynı user ile ikinci agent oluşturmaya çalış
        with self.assertRaises(IntegrityError):
            Agent.objects.create(
                user=self.agent_user,
                organisation=self.organisor_profile
            )
    
    def test_agent_cascade_delete_user(self):
        """Agent cascade delete user testi"""
        agent = Agent.objects.create(
            user=self.agent_user,
            organisation=self.organisor_profile
        )
        
        agent_id = agent.id
        user_id = self.agent_user.id
        
        # User'ı sil
        self.agent_user.delete()
        
        # Agent da silinmeli
        self.assertFalse(Agent.objects.filter(id=agent_id).exists())
        self.assertFalse(User.objects.filter(id=user_id).exists())
    
    def test_agent_cascade_delete_organisation(self):
        """Agent cascade delete organisation testi"""
        agent = Agent.objects.create(
            user=self.agent_user,
            organisation=self.organisor_profile
        )
        
        agent_id = agent.id
        
        # Organisation'ı sil
        self.organisor_profile.delete()
        
        # Agent da silinmeli
        self.assertFalse(Agent.objects.filter(id=agent_id).exists())


class TestEmailVerificationTokenModel(TestCase):
    """EmailVerificationToken model testleri"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='token_test',
            email='token_test@example.com',
            password='testpass123',
            first_name='Token',
            last_name='Test',
            phone_number='+905551111111',
            date_of_birth='1990-01-01',
            gender='M',
            is_agent=True,
            email_verified=False
        )
    
    def test_token_creation(self):
        """Token oluşturma testi"""
        token = EmailVerificationToken.objects.create(user=self.user)
        
        self.assertEqual(token.user, self.user)
        self.assertIsNotNone(token.token)
        self.assertFalse(token.is_used)
        self.assertIsNotNone(token.created_at)
    
    def test_token_str_representation(self):
        """Token __str__ metodu testi"""
        token = EmailVerificationToken.objects.create(user=self.user)
        
        expected_str = f"Verification token for {self.user.email}"
        self.assertEqual(str(token), expected_str)
    
    def test_token_uniqueness(self):
        """Token benzersizlik testi"""
        token1 = EmailVerificationToken.objects.create(user=self.user)
        token2 = EmailVerificationToken.objects.create(user=self.user)
        
        # Her iki token farklı olmalı
        self.assertNotEqual(token1.token, token2.token)
        
        # Aynı user için birden fazla token olabilir
        self.assertEqual(EmailVerificationToken.objects.filter(user=self.user).count(), 2)
    
    def test_token_expiration(self):
        """Token süresi dolma testi"""
        token = EmailVerificationToken.objects.create(user=self.user)
        
        # Yeni oluşturulan token süresi dolmamış olmalı
        self.assertFalse(token.is_expired())
        
        # Mock ile 25 saat sonrasını simüle et
        with patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = token.created_at + timedelta(hours=25)
            
            # Token süresi dolmuş olmalı
            self.assertTrue(token.is_expired())
    
    def test_token_is_used_default(self):
        """Token is_used default değeri testi"""
        token = EmailVerificationToken.objects.create(user=self.user)
        
        self.assertFalse(token.is_used)
    
    def test_token_cascade_delete_user(self):
        """Token cascade delete user testi"""
        token = EmailVerificationToken.objects.create(user=self.user)
        
        token_id = token.id
        user_id = self.user.id
        
        # User'ı sil
        self.user.delete()
        
        # Token da silinmeli
        self.assertFalse(EmailVerificationToken.objects.filter(id=token_id).exists())
        self.assertFalse(User.objects.filter(id=user_id).exists())
    
    def test_multiple_tokens_for_same_user(self):
        """Aynı kullanıcı için birden fazla token testi"""
        token1 = EmailVerificationToken.objects.create(user=self.user)
        token2 = EmailVerificationToken.objects.create(user=self.user)
        
        # Her iki token farklı olmalı
        self.assertNotEqual(token1.token, token2.token)
        
        # Aynı user'a ait olmalı
        self.assertEqual(token1.user, self.user)
        self.assertEqual(token2.user, self.user)
        
        # Toplam 2 token olmalı
        self.assertEqual(EmailVerificationToken.objects.filter(user=self.user).count(), 2)
    
    def test_token_used_status_update(self):
        """Token kullanıldı durumu güncelleme testi"""
        token = EmailVerificationToken.objects.create(user=self.user)
        
        # Başlangıçta kullanılmamış
        self.assertFalse(token.is_used)
        
        # Kullanıldı olarak işaretle
        token.is_used = True
        token.save()
        
        # Güncellenmiş token'ı al
        updated_token = EmailVerificationToken.objects.get(id=token.id)
        self.assertTrue(updated_token.is_used)


class TestCategoryModels(TestCase):
    """Category, SourceCategory, ValueCategory model testleri"""
    
    def setUp(self):
        """Set up test data"""
        # Organisor kullanıcısı oluştur
        self.organisor_user = User.objects.create_user(
            username='category_organisor_test',
            email='category_organisor_test@example.com',
            password='testpass123',
            first_name='Category',
            last_name='Organisor',
            phone_number='+905551234567',
            date_of_birth='1980-01-01',
            gender='M',
            is_organisor=True,
            email_verified=True
        )
        
        # UserProfile oluştur
        self.organisor_profile, created = UserProfile.objects.get_or_create(
            user=self.organisor_user
        )
    
    def test_category_creation(self):
        """Category oluşturma testi"""
        category = Category.objects.create(
            name="Electronics",
            organisation=self.organisor_profile
        )
        
        self.assertEqual(category.name, "Electronics")
        self.assertEqual(category.organisation, self.organisor_profile)
        self.assertEqual(str(category), "Electronics")
    
    def test_source_category_creation(self):
        """SourceCategory oluşturma testi"""
        source_category = SourceCategory.objects.create(
            name="Website",
            organisation=self.organisor_profile
        )
        
        self.assertEqual(source_category.name, "Website")
        self.assertEqual(source_category.organisation, self.organisor_profile)
        self.assertEqual(str(source_category), "Website")
    
    def test_value_category_creation(self):
        """ValueCategory oluşturma testi"""
        value_category = ValueCategory.objects.create(
            name="High Value",
            organisation=self.organisor_profile
        )
        
        self.assertEqual(value_category.name, "High Value")
        self.assertEqual(value_category.organisation, self.organisor_profile)
        self.assertEqual(str(value_category), "High Value")
    
    def test_category_organisation_relationship(self):
        """Category-organisation ilişkisi testi"""
        category = Category.objects.create(
            name="Test Category",
            organisation=self.organisor_profile
        )
        
        self.assertEqual(category.organisation, self.organisor_profile)
        self.assertEqual(category.organisation.user, self.organisor_user)
    
    def test_category_cascade_delete_organisation(self):
        """Category cascade delete organisation testi"""
        category = Category.objects.create(
            name="Test Category",
            organisation=self.organisor_profile
        )
        
        category_id = category.id
        
        # Organisation'ı sil
        self.organisor_profile.delete()
        
        # Category da silinmeli
        self.assertFalse(Category.objects.filter(id=category_id).exists())
    
    def test_source_category_cascade_delete_organisation(self):
        """SourceCategory cascade delete organisation testi"""
        source_category = SourceCategory.objects.create(
            name="Test Source",
            organisation=self.organisor_profile
        )
        
        source_category_id = source_category.id
        
        # Organisation'ı sil
        self.organisor_profile.delete()
        
        # SourceCategory da silinmeli
        self.assertFalse(SourceCategory.objects.filter(id=source_category_id).exists())
    
    def test_value_category_cascade_delete_organisation(self):
        """ValueCategory cascade delete organisation testi"""
        value_category = ValueCategory.objects.create(
            name="Test Value",
            organisation=self.organisor_profile
        )
        
        value_category_id = value_category.id
        
        # Organisation'ı sil
        self.organisor_profile.delete()
        
        # ValueCategory da silinmeli
        self.assertFalse(ValueCategory.objects.filter(id=value_category_id).exists())


class TestLeadModelSignals(TransactionTestCase):
    """Lead model signal testleri"""
    
    def setUp(self):
        """Set up test data"""
        # Organisor kullanıcısı oluştur
        self.organisor_user = User.objects.create_user(
            username='signal_organisor_test',
            email='signal_organisor_test@example.com',
            password='testpass123',
            first_name='Signal',
            last_name='Organisor',
            phone_number='+905551234567',
            date_of_birth='1980-01-01',
            gender='M',
            is_organisor=True,
            email_verified=True
        )
        
        # UserProfile oluştur
        self.organisor_profile, created = UserProfile.objects.get_or_create(
            user=self.organisor_user
        )
    
    def test_user_created_signal(self):
        """User oluşturma signal testi"""
        # Yeni user oluştur
        new_user = User.objects.create_user(
            username='signal_user_test',
            email='signal_user_test@example.com',
            password='testpass123',
            first_name='Signal',
            last_name='User',
            phone_number='+905559999999',
            date_of_birth='1990-01-01',
            gender='F',
            is_agent=True,
            email_verified=True
        )
        
        # UserProfile otomatik oluşturulmuş olmalı
        self.assertTrue(UserProfile.objects.filter(user=new_user).exists())
        
        # UserProfile doğru user'a ait olmalı
        user_profile = UserProfile.objects.get(user=new_user)
        self.assertEqual(user_profile.user, new_user)


class TestLeadModelIntegration(TestCase):
    """Lead model entegrasyon testleri"""
    
    def setUp(self):
        """Set up test data"""
        # Organisor kullanıcısı oluştur
        self.organisor_user = User.objects.create_user(
            username='integration_organisor_test',
            email='integration_organisor_test@example.com',
            password='testpass123',
            first_name='Integration',
            last_name='Organisor',
            phone_number='+905551234567',
            date_of_birth='1980-01-01',
            gender='M',
            is_organisor=True,
            email_verified=True
        )
        
        # UserProfile oluştur
        self.organisor_profile, created = UserProfile.objects.get_or_create(
            user=self.organisor_user
        )
        
        # Agent oluştur
        self.agent_user = User.objects.create_user(
            username='integration_agent_test',
            email='integration_agent_test@example.com',
            password='testpass123',
            first_name='Integration',
            last_name='Agent',
            phone_number='+905559876543',
            date_of_birth='1990-01-01',
            gender='F',
            is_agent=True,
            email_verified=True
        )
        
        self.agent = Agent.objects.create(
            user=self.agent_user,
            organisation=self.organisor_profile
        )
        
        # Kategoriler oluştur
        self.category = Category.objects.create(
            name="Integration Category",
            organisation=self.organisor_profile
        )
        
        self.source_category = SourceCategory.objects.create(
            name="Social Media",
            organisation=self.organisor_profile
        )
        
        self.value_category = ValueCategory.objects.create(
            name="Medium Value",
            organisation=self.organisor_profile
        )
    
    def test_lead_with_all_relationships(self):
        """Tüm ilişkilerle lead oluşturma testi"""
        lead = Lead.objects.create(
            first_name='Integration',
            last_name='Lead',
            age=35,
            organisation=self.organisor_profile,
            agent=self.agent,
            category=self.category,
            source_category=self.source_category,
            value_category=self.value_category,
            description='Integration test lead',
            phone_number='+905555555555',
            email='integration.lead@example.com',
            address='789 Integration Street'
        )
        
        # Tüm ilişkiler doğru mu
        self.assertEqual(lead.organisation, self.organisor_profile)
        self.assertEqual(lead.agent, self.agent)
        self.assertEqual(lead.category, self.category)
        self.assertEqual(lead.source_category, self.source_category)
        self.assertEqual(lead.value_category, self.value_category)
        
        # Agent'ın organisation'ı doğru mu
        self.assertEqual(lead.agent.organisation, self.organisor_profile)
        
        # Kategorilerin organisation'ı doğru mu
        self.assertEqual(lead.category.organisation, self.organisor_profile)
        self.assertEqual(lead.source_category.organisation, self.organisor_profile)
        self.assertEqual(lead.value_category.organisation, self.organisor_profile)
    
    def test_lead_agent_lead_relationship(self):
        """Lead-agent-lead ilişkisi testi"""
        # Birden fazla lead aynı agent'a atanabilir
        lead1 = Lead.objects.create(
            first_name='Lead1',
            last_name='Test',
            age=25,
            organisation=self.organisor_profile,
            agent=self.agent,
            description='First lead',
            phone_number='+905551111111',
            email='lead1@example.com',
            address='123 First Street'
        )
        
        lead2 = Lead.objects.create(
            first_name='Lead2',
            last_name='Test',
            age=30,
            organisation=self.organisor_profile,
            agent=self.agent,
            description='Second lead',
            phone_number='+905552222222',
            email='lead2@example.com',
            address='456 Second Street'
        )
        
        # Her iki lead aynı agent'a ait olmalı
        self.assertEqual(lead1.agent, self.agent)
        self.assertEqual(lead2.agent, self.agent)
        
        # Agent'dan lead'lere erişim
        agent_leads = Lead.objects.filter(agent=self.agent)
        self.assertEqual(agent_leads.count(), 2)
        self.assertIn(lead1, agent_leads)
        self.assertIn(lead2, agent_leads)
    
    def test_lead_category_lead_relationship(self):
        """Lead-category-lead ilişkisi testi"""
        # Birden fazla lead aynı kategorilere atanabilir
        lead1 = Lead.objects.create(
            first_name='Lead1',
            last_name='Test',
            age=25,
            organisation=self.organisor_profile,
            category=self.category,
            source_category=self.source_category,
            value_category=self.value_category,
            description='First lead',
            phone_number='+905551111111',
            email='lead1@example.com',
            address='123 First Street'
        )
        
        lead2 = Lead.objects.create(
            first_name='Lead2',
            last_name='Test',
            age=30,
            organisation=self.organisor_profile,
            category=self.category,
            source_category=self.source_category,
            value_category=self.value_category,
            description='Second lead',
            phone_number='+905552222222',
            email='lead2@example.com',
            address='456 Second Street'
        )
        
        # Her iki lead aynı kategorilere ait olmalı
        self.assertEqual(lead1.category, self.category)
        self.assertEqual(lead2.category, self.category)
        self.assertEqual(lead1.source_category, self.source_category)
        self.assertEqual(lead2.source_category, self.source_category)
        self.assertEqual(lead1.value_category, self.value_category)
        self.assertEqual(lead2.value_category, self.value_category)
        
        # Kategorilerden lead'lere erişim
        category_leads = self.category.leads.all()
        self.assertEqual(category_leads.count(), 2)
        self.assertIn(lead1, category_leads)
        self.assertIn(lead2, category_leads)


if __name__ == "__main__":
    print("Leads Models Testleri Başlatılıyor...")
    print("=" * 60)
    
    # Test çalıştırma
    import unittest
    unittest.main()
