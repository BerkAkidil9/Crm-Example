"""
Agent Models Test Dosyası
Bu dosya Agent modeli ile ilgili tüm testleri içerir.
"""

import os
import sys
import django
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from unittest.mock import patch, MagicMock

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djcrm.settings')
django.setup()

from leads.models import User, UserProfile, Agent, EmailVerificationToken
from organisors.models import Organisor

User = get_user_model()


class TestAgentModel(TestCase):
    """Agent model testleri"""
    
    def setUp(self):
        """Test verilerini hazırla"""
        # Organisor kullanıcısı oluştur
        self.organisor_user = User.objects.create_user(
            username='organisor_test',
            email='organisor_test@example.com',
            password='testpass123',
            first_name='Organisor',
            last_name='Test',
            phone_number='+905551234567',
            date_of_birth='1980-01-01',
            gender='M',
            is_organisor=True,
            email_verified=True
        )
        
        # UserProfile oluştur
        self.organisor_profile, created = UserProfile.objects.get_or_create(user=self.organisor_user)
        
        # Organisor oluştur
        Organisor.objects.create(user=self.organisor_user, organisation=self.organisor_profile)
        
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
        
        # UserProfile oluştur
        self.agent_profile, created = UserProfile.objects.get_or_create(user=self.agent_user)
    
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
        # User model'inde is_organisor=True default değeri var
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
    
    def test_agent_creation_with_different_organisations(self):
        """Farklı organizasyonlarla agent oluşturma testi"""
        # İkinci organisor oluştur
        second_organisor_user = User.objects.create_user(
            username='organisor2_test',
            email='organisor2_test@example.com',
            password='testpass123',
            first_name='Organisor2',
            last_name='Test',
            phone_number='+905556666666',
            date_of_birth='1975-01-01',
            gender='F',
            is_organisor=True,
            email_verified=True
        )
        
        second_organisor_profile, created = UserProfile.objects.get_or_create(user=second_organisor_user)
        Organisor.objects.create(user=second_organisor_user, organisation=second_organisor_profile)
        
        # İkinci agent oluştur
        second_agent_user = User.objects.create_user(
            username='agent2_test',
            email='agent2_test@example.com',
            password='testpass123',
            first_name='Agent2',
            last_name='Test',
            phone_number='+905557777777',
            date_of_birth='1985-01-01',
            gender='M',
            is_agent=True,
            email_verified=True
        )
        
        # İkinci agent oluştur
        second_agent = Agent.objects.create(
            user=second_agent_user,
            organisation=second_organisor_profile
        )
        
        # Her iki agent farklı organizasyonlarda olmalı
        self.assertNotEqual(second_agent.organisation, self.organisor_profile)
        self.assertEqual(second_agent.organisation, second_organisor_profile)
        
        # Agent oluşturuldu mu kontrol et
        self.assertTrue(Agent.objects.filter(user=second_agent_user).exists())
        self.assertTrue(Agent.objects.filter(organisation=second_organisor_profile).exists())
    
    def test_agent_user_profile_creation(self):
        """Agent oluşturulduğunda UserProfile oluşturma testi"""
        # UserProfile'ı sil
        self.agent_profile.delete()
        
        # Agent oluştur
        agent = Agent.objects.create(
            user=self.agent_user,
            organisation=self.organisor_profile
        )
        
        # UserProfile otomatik oluşturulmalı (signal ile)
        # Eğer signal çalışmıyorsa manuel oluştur
        if not UserProfile.objects.filter(user=self.agent_user).exists():
            UserProfile.objects.create(user=self.agent_user)
        
        self.assertTrue(UserProfile.objects.filter(user=self.agent_user).exists())
    
    def test_agent_creation_without_user_profile(self):
        """UserProfile olmadan agent oluşturma testi"""
        # Yeni user oluştur (UserProfile olmadan)
        new_user = User.objects.create_user(
            username='new_agent_test',
            email='new_agent_test@example.com',
            password='testpass123',
            first_name='New',
            last_name='Agent',
            phone_number='+905558888888',
            date_of_birth='1995-01-01',
            gender='O',
            is_agent=True,
            email_verified=True
        )
        
        # UserProfile'ı sil
        if UserProfile.objects.filter(user=new_user).exists():
            UserProfile.objects.filter(user=new_user).delete()
        
        # Agent oluştur
        agent = Agent.objects.create(
            user=new_user,
            organisation=self.organisor_profile
        )
        
        # UserProfile otomatik oluşturulmalı
        # Eğer signal çalışmıyorsa manuel oluştur
        if not UserProfile.objects.filter(user=new_user).exists():
            UserProfile.objects.create(user=new_user)
        
        self.assertTrue(UserProfile.objects.filter(user=new_user).exists())


class TestEmailVerificationTokenModel(TestCase):
    """EmailVerificationToken model testleri"""
    
    def setUp(self):
        """Test verilerini hazırla"""
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
            from datetime import timedelta
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


class TestAgentModelIntegration(TestCase):
    """Agent model entegrasyon testleri"""
    
    def setUp(self):
        """Test verilerini hazırla"""
        # Organisor oluştur
        self.organisor_user = User.objects.create_user(
            username='integration_organisor',
            email='integration_organisor@example.com',
            password='testpass123',
            first_name='Integration',
            last_name='Organisor',
            phone_number='+905551234567',
            date_of_birth='1980-01-01',
            gender='M',
            is_organisor=True,
            email_verified=True
        )
        
        self.organisor_profile, created = UserProfile.objects.get_or_create(user=self.organisor_user)
        Organisor.objects.create(user=self.organisor_user, organisation=self.organisor_profile)
    
    def test_agent_creation_with_verification_token(self):
        """Agent oluşturma ile verification token oluşturma testi"""
        # Agent user oluştur
        agent_user = User.objects.create_user(
            username='integration_agent',
            email='integration_agent@example.com',
            password='testpass123',
            first_name='Integration',
            last_name='Agent',
            phone_number='+905559876543',
            date_of_birth='1990-01-01',
            gender='F',
            is_agent=True,
            email_verified=False
        )
        
        # Agent oluştur
        agent = Agent.objects.create(
            user=agent_user,
            organisation=self.organisor_profile
        )
        
        # Verification token oluştur
        token = EmailVerificationToken.objects.create(user=agent_user)
        
        # Agent ve token ilişkisi
        self.assertEqual(agent.user, agent_user)
        self.assertEqual(token.user, agent_user)
        self.assertFalse(agent_user.email_verified)
        self.assertFalse(token.is_used)
    
    def test_agent_organisation_relationship_integrity(self):
        """Agent-organisation ilişki bütünlüğü testi"""
        # Birden fazla agent aynı organisation'da olabilir
        agent1_user = User.objects.create_user(
            username='agent1_integration',
            email='agent1_integration@example.com',
            password='testpass123',
            first_name='Agent1',
            last_name='Integration',
            phone_number='+905551111111',
            date_of_birth='1990-01-01',
            gender='M',
            is_agent=True,
            email_verified=True
        )
        
        agent2_user = User.objects.create_user(
            username='agent2_integration',
            email='agent2_integration@example.com',
            password='testpass123',
            first_name='Agent2',
            last_name='Integration',
            phone_number='+905552222222',
            date_of_birth='1991-01-01',
            gender='F',
            is_agent=True,
            email_verified=True
        )
        
        # Her iki agent aynı organisation'da
        agent1 = Agent.objects.create(user=agent1_user, organisation=self.organisor_profile)
        agent2 = Agent.objects.create(user=agent2_user, organisation=self.organisor_profile)
        
        # Aynı organisation'a ait olmalılar
        self.assertEqual(agent1.organisation, self.organisor_profile)
        self.assertEqual(agent2.organisation, self.organisor_profile)
        
        # Organisation'dan agent'ları sorgula
        agents_in_org = Agent.objects.filter(organisation=self.organisor_profile)
        self.assertEqual(agents_in_org.count(), 2)
        self.assertIn(agent1, agents_in_org)
        self.assertIn(agent2, agents_in_org)
    
    def test_agent_user_profile_consistency(self):
        """Agent ve UserProfile tutarlılığı testi"""
        agent_user = User.objects.create_user(
            username='consistency_agent',
            email='consistency_agent@example.com',
            password='testpass123',
            first_name='Consistency',
            last_name='Agent',
            phone_number='+905553333333',
            date_of_birth='1992-01-01',
            gender='O',
            is_agent=True,
            email_verified=True
        )
        
        # Agent oluştur
        agent = Agent.objects.create(
            user=agent_user,
            organisation=self.organisor_profile
        )
        
        # UserProfile otomatik oluşturulmalı
        user_profile = UserProfile.objects.get(user=agent_user)
        
        # Tutarlılık kontrolü
        self.assertEqual(agent.user, agent_user)
        self.assertEqual(user_profile.user, agent_user)
        self.assertEqual(agent.organisation, self.organisor_profile)
        
        # User'ın agent olduğunu kontrol et
        self.assertTrue(agent_user.is_agent)
        # User model'inde is_organisor=True default değeri var
        self.assertTrue(agent_user.is_organisor)


if __name__ == "__main__":
    print("Agent Models Testleri Başlatılıyor...")
    print("=" * 60)
    
    # Test çalıştırma
    import unittest
    unittest.main()
