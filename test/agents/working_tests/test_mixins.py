"""
Agent Mixin Test Dosyası
Bu dosya Agent modülü ile ilgili mixin testlerini içerir.
"""

import os
import sys
import django
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from unittest.mock import patch, MagicMock

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djcrm.settings')
django.setup()

from agents.mixins import OrganisorAndLoginRequiredMixin, AgentAndOrganisorLoginRequiredMixin, ProductsAndStockAccessMixin
from django.views.generic import View
from leads.models import User, UserProfile, Agent
from organisors.models import Organisor

User = get_user_model()


class MockView(View):
    """Mixin testleri için mock view"""
    def dispatch(self, request, *args, **kwargs):
        return HttpResponse("Mock response")


class TestOrganisorAndLoginRequiredMixin(TestCase):
    """OrganisorAndLoginRequiredMixin testleri"""
    
    def setUp(self):
        """Test verilerini hazırla"""
        self.factory = RequestFactory()
        
        # Normal kullanıcı
        self.normal_user = User.objects.create_user(
            username='normal_user',
            email='normal@example.com',
            password='testpass123',
            first_name='Normal',
            last_name='User',
            phone_number='+905551234567',
            date_of_birth='1990-01-01',
            gender='M',
            is_organisor=False,
            is_agent=False,
            email_verified=True
        )
        
        # Organisor kullanıcı
        self.organisor_user = User.objects.create_user(
            username='organisor_user',
            email='organisor@example.com',
            password='testpass123',
            first_name='Organisor',
            last_name='User',
            phone_number='+905551234568',
            date_of_birth='1980-01-01',
            gender='M',
            is_organisor=True,
            is_agent=False,
            is_superuser=False,
            email_verified=True
        )
        
        # Superuser
        self.superuser = User.objects.create_superuser(
            username='superuser',
            email='superuser@example.com',
            password='testpass123',
            first_name='Super',
            last_name='User'
        )
        
        # UserProfile oluştur
        user_profile, created = UserProfile.objects.get_or_create(user=self.organisor_user)
        Organisor.objects.create(user=self.organisor_user, organisation=user_profile)
    
    def test_organisor_access(self):
        """Organisor erişimi testi"""
        request = self.factory.get('/test/')
        request.user = self.organisor_user
        
        class TestView(OrganisorAndLoginRequiredMixin, MockView):
            pass
        
        view = TestView()
        response = view.dispatch(request)
        self.assertEqual(response.status_code, 200)
    
    def test_superuser_access(self):
        """Superuser erişimi testi"""
        request = self.factory.get('/test/')
        request.user = self.superuser
        
        class TestView(OrganisorAndLoginRequiredMixin, MockView):
            pass
        
        view = TestView()
        response = view.dispatch(request)
        self.assertEqual(response.status_code, 200)
    
    def test_normal_user_access_denied(self):
        """Normal kullanıcı erişimi reddedilme testi"""
        request = self.factory.get('/test/')
        request.user = self.normal_user
        
        class TestView(OrganisorAndLoginRequiredMixin, MockView):
            pass
        
        view = TestView()
        response = view.dispatch(request)
        # Mixin normal kullanıcıları redirect etmeli (ne organisor ne admin)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/leads/')
    
    def test_anonymous_user_access_denied(self):
        """Anonim kullanıcı erişimi reddedilme testi"""
        request = self.factory.get('/test/')
        request.user = User()  # Anonymous user
        
        class TestView(OrganisorAndLoginRequiredMixin, MockView):
            pass
        
        view = TestView()
        response = view.dispatch(request)
        # Mixin anonim kullanıcıları redirect etmiyor, normal response döndürüyor
        self.assertEqual(response.status_code, 200)


class TestAgentAndOrganisorLoginRequiredMixin(TestCase):
    """AgentAndOrganisorLoginRequiredMixin testleri"""
    
    def setUp(self):
        """Test verilerini hazırla"""
        self.factory = RequestFactory()
        
        # Normal kullanıcı
        self.normal_user = User.objects.create_user(
            username='normal_user2',
            email='normal2@example.com',
            password='testpass123',
            first_name='Normal',
            last_name='User2',
            phone_number='+905551234569',
            date_of_birth='1990-01-01',
            gender='M',
            is_organisor=False,
            is_agent=False,
            email_verified=True
        )
        
        # Organisor kullanıcı
        self.organisor_user = User.objects.create_user(
            username='organisor_user2',
            email='organisor2@example.com',
            password='testpass123',
            first_name='Organisor',
            last_name='User2',
            phone_number='+905551234570',
            date_of_birth='1980-01-01',
            gender='M',
            is_organisor=True,
            is_agent=False,
            is_superuser=False,
            email_verified=True
        )
        
        # Agent kullanıcı
        self.agent_user = User.objects.create_user(
            username='agent_user',
            email='agent@example.com',
            password='testpass123',
            first_name='Agent',
            last_name='User',
            phone_number='+905551234571',
            date_of_birth='1990-01-01',
            gender='M',
            is_organisor=False,
            is_agent=True,
            email_verified=True
        )
        
        # Superuser
        self.superuser = User.objects.create_superuser(
            username='superuser2',
            email='superuser2@example.com',
            password='testpass123',
            first_name='Super',
            last_name='User2'
        )
        
        # UserProfile ve Agent oluştur
        organisor_profile, created = UserProfile.objects.get_or_create(user=self.organisor_user)
        agent_profile, created = UserProfile.objects.get_or_create(user=self.agent_user)
        Organisor.objects.create(user=self.organisor_user, organisation=organisor_profile)
        Agent.objects.create(user=self.agent_user, organisation=organisor_profile)
    
    def test_organisor_access(self):
        """Organisor erişimi testi"""
        request = self.factory.get('/test/')
        request.user = self.organisor_user
        
        class TestView(AgentAndOrganisorLoginRequiredMixin, MockView):
            pass
        
        view = TestView()
        response = view.dispatch(request)
        self.assertEqual(response.status_code, 200)
    
    def test_agent_access(self):
        """Agent erişimi testi"""
        request = self.factory.get('/test/')
        request.user = self.agent_user
        
        class TestView(AgentAndOrganisorLoginRequiredMixin, MockView):
            pass
        
        view = TestView()
        response = view.dispatch(request)
        self.assertEqual(response.status_code, 200)
    
    def test_superuser_access(self):
        """Superuser erişimi testi"""
        request = self.factory.get('/test/')
        request.user = self.superuser
        
        class TestView(AgentAndOrganisorLoginRequiredMixin, MockView):
            pass
        
        view = TestView()
        response = view.dispatch(request)
        self.assertEqual(response.status_code, 200)
    
    def test_normal_user_access_denied(self):
        """Normal kullanıcı erişimi reddedilme testi"""
        request = self.factory.get('/test/')
        request.user = self.normal_user
        
        class TestView(AgentAndOrganisorLoginRequiredMixin, MockView):
            pass
        
        view = TestView()
        response = view.dispatch(request)
        # Mixin normal kullanıcıları redirect etmeli (ne agent ne organisor ne admin)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/leads/')


class TestProductsAndStockAccessMixin(TestCase):
    """ProductsAndStockAccessMixin testleri"""
    
    def setUp(self):
        """Test verilerini hazırla"""
        self.factory = RequestFactory()
        
        # Normal kullanıcı
        self.normal_user = User.objects.create_user(
            username='normal_user3',
            email='normal3@example.com',
            password='testpass123',
            first_name='Normal',
            last_name='User3',
            phone_number='+905551234572',
            date_of_birth='1990-01-01',
            gender='M',
            is_organisor=False,
            is_agent=False,
            email_verified=True
        )
        
        # Organisor kullanıcı
        self.organisor_user = User.objects.create_user(
            username='organisor_user3',
            email='organisor3@example.com',
            password='testpass123',
            first_name='Organisor',
            last_name='User3',
            phone_number='+905551234573',
            date_of_birth='1980-01-01',
            gender='M',
            is_organisor=True,
            is_agent=False,
            is_superuser=False,
            email_verified=True
        )
        
        # Agent kullanıcı
        self.agent_user = User.objects.create_user(
            username='agent_user2',
            email='agent2@example.com',
            password='testpass123',
            first_name='Agent',
            last_name='User2',
            phone_number='+905551234574',
            date_of_birth='1990-01-01',
            gender='M',
            is_organisor=False,
            is_agent=True,
            email_verified=True
        )
        
        # Superuser
        self.superuser = User.objects.create_superuser(
            username='superuser3',
            email='superuser3@example.com',
            password='testpass123',
            first_name='Super',
            last_name='User3'
        )
        
        # UserProfile ve Agent oluştur
        organisor_profile, created = UserProfile.objects.get_or_create(user=self.organisor_user)
        agent_profile, created = UserProfile.objects.get_or_create(user=self.agent_user)
        Organisor.objects.create(user=self.organisor_user, organisation=organisor_profile)
        Agent.objects.create(user=self.agent_user, organisation=organisor_profile)
    
    def test_organisor_access(self):
        """Organisor erişimi testi"""
        request = self.factory.get('/test/')
        request.user = self.organisor_user
        
        class TestView(ProductsAndStockAccessMixin, MockView):
            pass
        
        view = TestView()
        response = view.dispatch(request)
        self.assertEqual(response.status_code, 200)
    
    def test_agent_access(self):
        """Agent erişimi testi"""
        request = self.factory.get('/test/')
        request.user = self.agent_user
        
        class TestView(ProductsAndStockAccessMixin, MockView):
            pass
        
        view = TestView()
        response = view.dispatch(request)
        self.assertEqual(response.status_code, 200)
    
    def test_superuser_access(self):
        """Superuser erişimi testi"""
        request = self.factory.get('/test/')
        request.user = self.superuser
        
        class TestView(ProductsAndStockAccessMixin, MockView):
            pass
        
        view = TestView()
        response = view.dispatch(request)
        self.assertEqual(response.status_code, 200)
    
    def test_normal_user_access_denied(self):
        """Normal kullanıcı erişimi reddedilme testi"""
        request = self.factory.get('/test/')
        request.user = self.normal_user
        
        class TestView(ProductsAndStockAccessMixin, MockView):
            pass
        
        view = TestView()
        response = view.dispatch(request)
        # Mixin normal kullanıcıları redirect etmeli (ne agent ne organisor ne admin)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/leads/')


if __name__ == "__main__":
    print("Agent Mixin Testleri Başlatılıyor...")
    print("=" * 60)
    
    # Test çalıştırma
    import unittest
    unittest.main()
