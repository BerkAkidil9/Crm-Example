"""
Agent Forms Test File
This file tests all forms related to Agent.
"""

import os
import sys
import django
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core import mail
from unittest.mock import patch, MagicMock

# Load Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djcrm.settings')
django.setup()

from agents.forms import AgentModelForm, AgentCreateForm, AdminAgentCreateForm
from leads.models import User, UserProfile, Agent, EmailVerificationToken
from organisors.models import Organisor

User = get_user_model()


class TestAgentModelForm(TestCase):
    """AgentModelForm testleri"""
    
    def setUp(self):
        """Set up test data"""
        # Create organisor
        self.organisor_user = User.objects.create_user(
            username='organisor_forms',
            email='organisor_forms@example.com',
            password='testpass123',
            first_name='Organisor',
            last_name='Forms',
            phone_number='+905551234567',
            date_of_birth='1980-01-01',
            gender='M',
            is_organisor=True,
            email_verified=True
        )
        
        self.organisor_profile, created = UserProfile.objects.get_or_create(user=self.organisor_user)
        Organisor.objects.create(user=self.organisor_user, organisation=self.organisor_profile)
        
        # Create agent
        self.agent_user = User.objects.create_user(
            username='agent_forms',
            email='agent_forms@example.com',
            password='testpass123',
            first_name='Agent',
            last_name='Forms',
            phone_number='+905559876543',
            date_of_birth='1990-01-01',
            gender='F',
            is_agent=True,
            email_verified=True
        )
        
        self.agent_profile, created = UserProfile.objects.get_or_create(user=self.agent_user)
        self.agent = Agent.objects.create(user=self.agent_user, organisation=self.organisor_profile)
        
        self.valid_data = {
            'username': 'agent_forms',
            'email': 'agent_forms@example.com',
            'first_name': 'Agent',
            'last_name': 'Forms',
            'phone_number_0': '+90',
            'phone_number_1': '5559876543',
            'date_of_birth': '1990-01-01',
            'gender': 'F',
            'password1': '',
            'password2': ''
        }
    
    def test_form_initialization(self):
        """Form initialization test"""
        form = AgentModelForm(instance=self.agent_user)
        
        # Check presence of required fields
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
        """Form test with valid data"""
        form = AgentModelForm(data=self.valid_data, instance=self.agent_user)
        self.assertTrue(form.is_valid())
    
    def test_form_required_fields(self):
        """Zorunlu alanlar testi"""
        # AgentModelForm'da sadece email required
        required_fields = ['email']
        
        for field in required_fields:
            data = self.valid_data.copy()
            del data[field]
            
            form = AgentModelForm(data=data, instance=self.agent_user)
            self.assertFalse(form.is_valid())
            self.assertIn(field, form.errors)
    
    def test_form_email_validation_unique(self):
        """Email benzersizlik validasyonu testi"""
        # Başka bir kullanıcı oluştur
        other_user = User.objects.create_user(
            username='other_user',
            email='other@example.com',
            password='testpass123'
        )
        
        # Aynı email ile form oluştur
        data = self.valid_data.copy()
        data['email'] = 'other@example.com'
        
        form = AgentModelForm(data=data, instance=self.agent_user)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertIn('already exists', str(form.errors['email']))
    
    def test_form_username_validation_unique(self):
        """Kullanıcı adı benzersizlik validasyonu testi"""
        # Başka bir kullanıcı oluştur
        other_user = User.objects.create_user(
            username='other_user',
            email='other@example.com',
            password='testpass123'
        )
        
        # Aynı kullanıcı adı ile form oluştur
        data = self.valid_data.copy()
        data['username'] = 'other_user'
        
        form = AgentModelForm(data=data, instance=self.agent_user)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertIn('already exists', str(form.errors['username']))
    
    def test_form_phone_number_validation_unique(self):
        """Telefon numarası benzersizlik validasyonu testi"""
        # Başka bir kullanıcı oluştur
        other_user = User.objects.create_user(
            username='other_user',
            email='other@example.com',
            password='testpass123',
            phone_number='+905556666666'
        )
        
        # Aynı telefon numarası ile form oluştur
        data = self.valid_data.copy()
        data['phone_number_0'] = '+90'
        data['phone_number_1'] = '5556666666'
        
        form = AgentModelForm(data=data, instance=self.agent_user)
        self.assertFalse(form.is_valid())
        self.assertIn('phone_number', form.errors)
        self.assertIn('already exists', str(form.errors['phone_number']))
    
    def test_form_password_validation(self):
        """Şifre validasyonu testi"""
        # Farklı şifreler
        data = self.valid_data.copy()
        data['password1'] = 'newpass123!'
        data['password2'] = 'differentpass123!'
        
        form = AgentModelForm(data=data, instance=self.agent_user)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
        self.assertIn("didn't match", str(form.errors['password2']).replace('&#x27;', "'"))
    
    def test_form_password_optional(self):
        """Şifre alanları opsiyonel testi"""
        # Şifre alanları boş bırakılabilir
        data = self.valid_data.copy()
        data['password1'] = ''
        data['password2'] = ''
        
        form = AgentModelForm(data=data, instance=self.agent_user)
        self.assertTrue(form.is_valid())
    
    def test_form_password_validation_short(self):
        """Kısa şifre validasyonu testi"""
        data = self.valid_data.copy()
        data['password1'] = '123'
        data['password2'] = '123'
        
        form = AgentModelForm(data=data, instance=self.agent_user)
        self.assertFalse(form.is_valid())
        self.assertIn('password1', form.errors)
    
    def test_form_password_validation_common(self):
        """Yaygın şifre validasyonu testi"""
        data = self.valid_data.copy()
        data['password1'] = 'password'
        data['password2'] = 'password'
        
        form = AgentModelForm(data=data, instance=self.agent_user)
        self.assertFalse(form.is_valid())
        self.assertIn('password1', form.errors)
    
    def test_form_widget_attributes(self):
        """Widget attributes test"""
        form = AgentModelForm(instance=self.agent_user)
        
        # Check CSS classes and placeholder
        self.assertIn('placeholder="Username"', str(form['username'].as_widget()))
        self.assertIn('placeholder="Enter email address"', str(form['email'].as_widget()))
        self.assertIn('placeholder="First Name"', str(form['first_name'].as_widget()))
        self.assertIn('placeholder="Last Name"', str(form['last_name'].as_widget()))
    
    def test_form_save_method(self):
        """Form save metodu testi"""
        data = self.valid_data.copy()
        data['password1'] = 'newpassword123!'
        data['password2'] = 'newpassword123!'
        
        form = AgentModelForm(data=data, instance=self.agent_user)
        self.assertTrue(form.is_valid())
        
        user = form.save()
        
        # Kullanıcı alanları doğru mu
        self.assertEqual(user.username, 'agent_forms')
        self.assertEqual(user.email, 'agent_forms@example.com')
        self.assertEqual(user.first_name, 'Agent')
        self.assertEqual(user.last_name, 'Forms')
        
        # Şifre değişti mi
        self.assertTrue(user.check_password('newpassword123!'))
    
    def test_form_save_without_password_change(self):
        """Şifre değiştirmeden form save testi"""
        data = self.valid_data.copy()
        data['password1'] = ''
        data['password2'] = ''
        
        form = AgentModelForm(data=data, instance=self.agent_user)
        self.assertTrue(form.is_valid())
        
        user = form.save()
        
        # Eski şifre korunmalı
        self.assertTrue(user.check_password('testpass123'))
    
    def test_form_clean_methods(self):
        """Form clean metodları testi"""
        # Email clean
        form = AgentModelForm(data=self.valid_data, instance=self.agent_user)
        if form.is_valid():
            cleaned_email = form.clean_email()
            self.assertEqual(cleaned_email, 'agent_forms@example.com')
        
        # Username clean
        form = AgentModelForm(data=self.valid_data, instance=self.agent_user)
        if form.is_valid():
            cleaned_username = form.clean_username()
            self.assertEqual(cleaned_username, 'agent_forms')
    
    def test_form_validation_edge_cases(self):
        """Form validasyon sınır durumları testi"""
        # Geçersiz email formatı
        data = self.valid_data.copy()
        data['email'] = 'invalid-email'
        form = AgentModelForm(data=data, instance=self.agent_user)
        self.assertFalse(form.is_valid())
        
        # Geçersiz tarih formatı
        data = self.valid_data.copy()
        data['date_of_birth'] = 'invalid-date'
        form = AgentModelForm(data=data, instance=self.agent_user)
        self.assertFalse(form.is_valid())
    
    def test_form_field_help_texts(self):
        """Form alan yardım metinleri testi"""
        form = AgentModelForm(instance=self.agent_user)
        
        self.assertEqual(form.fields['email'].help_text, "Email address is required")
        self.assertIn("At least 8 characters", form.fields['password1'].help_text)
        self.assertIn("Enter the same password as above", form.fields['password2'].help_text)
    
    def test_form_field_widgets(self):
        """Form alan widget'ları testi"""
        form = AgentModelForm(instance=self.agent_user)
        
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


class TestAgentCreateForm(TestCase):
    """AgentCreateForm testleri"""
    
    def setUp(self):
        """Set up test data"""
        self.valid_data = {
            'username': 'new_agent_forms',
            'email': 'new_agent_forms@example.com',
            'first_name': 'New',
            'last_name': 'Agent',
            'phone_number_0': '+90',
            'phone_number_1': '5551234568',
            'date_of_birth': '1990-01-01',
            'gender': 'M',
            'password1': 'testpass123!',
            'password2': 'testpass123!'
        }
    
    def test_form_initialization(self):
        """Form initialization test"""
        form = AgentCreateForm()
        
        # Check presence of required fields
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
        """Form test with valid data"""
        form = AgentCreateForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
    
    def test_form_required_fields(self):
        """Zorunlu alanlar testi"""
        # AgentCreateForm'da sadece email, phone_number, password1, password2 required
        required_fields = ['email', 'password1', 'password2']
        
        for field in required_fields:
            data = self.valid_data.copy()
            del data[field]
            
            form = AgentCreateForm(data=data)
            self.assertFalse(form.is_valid())
            self.assertIn(field, form.errors)
        
        # Phone number için özel kontrol
        data = self.valid_data.copy()
        del data['phone_number_0']
        del data['phone_number_1']
        form = AgentCreateForm(data=data)
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
        
        form = AgentCreateForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertIn('already exists', str(form.errors['email']))
    
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
        
        form = AgentCreateForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertIn('already exists', str(form.errors['username']))
    
    def test_form_phone_number_validation_unique(self):
        """Telefon numarası benzersizlik validasyonu testi"""
        # Önce bir kullanıcı oluştur
        User.objects.create_user(
            username='existing_user',
            email='existing@example.com',
            password='testpass123',
            phone_number='+905556666666'
        )
        
        # Aynı telefon numarası ile form oluştur
        data = self.valid_data.copy()
        data['phone_number_0'] = '+90'
        data['phone_number_1'] = '5556666666'
        
        form = AgentCreateForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('phone_number', form.errors)
        self.assertIn('already exists', str(form.errors['phone_number']))
    
    def test_form_password_validation(self):
        """Şifre validasyonu testi"""
        # Farklı şifreler
        data = self.valid_data.copy()
        data['password1'] = 'testpass123!'
        data['password2'] = 'differentpass123!'
        
        form = AgentCreateForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
        self.assertIn("didn't match", str(form.errors['password2']).replace('&#x27;', "'"))
    
    def test_form_save_method(self):
        """Form save metodu testi"""
        form = AgentCreateForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
        
        user = form.save()
        
        # Kullanıcı alanları doğru mu
        self.assertEqual(user.username, 'new_agent_forms')
        self.assertEqual(user.email, 'new_agent_forms@example.com')
        self.assertEqual(user.first_name, 'New')
        self.assertEqual(user.last_name, 'Agent')
        
        # Şifre doğru set edildi mi
        self.assertTrue(user.check_password('testpass123!'))
    
    def test_form_widget_attributes(self):
        """Widget attributes test"""
        form = AgentCreateForm()
        
        # Check CSS classes and placeholder
        self.assertIn('placeholder="Username"', str(form['username'].as_widget()))
        self.assertIn('placeholder="Enter email address"', str(form['email'].as_widget()))
        self.assertIn('placeholder="First Name"', str(form['first_name'].as_widget()))
        self.assertIn('placeholder="Last Name"', str(form['last_name'].as_widget()))


class TestAdminAgentCreateForm(TestCase):
    """AdminAgentCreateForm testleri"""
    
    def setUp(self):
        """Set up test data"""
        # Create organisor
        self.organisor_user = User.objects.create_user(
            username='admin_organisor',
            email='admin_organisor@example.com',
            password='testpass123',
            first_name='Admin',
            last_name='Organisor',
            phone_number='+905551234567',
            date_of_birth='1980-01-01',
            gender='M',
            is_organisor=True,
            email_verified=True
        )
        
        self.organisor_profile, created = UserProfile.objects.get_or_create(user=self.organisor_user)
        Organisor.objects.create(user=self.organisor_user, organisation=self.organisor_profile)
        
        self.valid_data = {
            'username': 'admin_agent_forms',
            'email': 'admin_agent_forms@example.com',
            'first_name': 'Admin',
            'last_name': 'Agent',
            'phone_number_0': '+90',
            'phone_number_1': '5551234568',
            'date_of_birth': '1990-01-01',
            'gender': 'M',
            'organisation': self.organisor_profile.id,
            'password1': 'testpass123!',
            'password2': 'testpass123!'
        }
    
    def test_form_initialization(self):
        """Form initialization test"""
        form = AdminAgentCreateForm()
        
        # Check presence of required fields
        self.assertIn('username', form.fields)
        self.assertIn('email', form.fields)
        self.assertIn('first_name', form.fields)
        self.assertIn('last_name', form.fields)
        self.assertIn('phone_number', form.fields)
        self.assertIn('date_of_birth', form.fields)
        self.assertIn('gender', form.fields)
        self.assertIn('organisation', form.fields)
        self.assertIn('password1', form.fields)
        self.assertIn('password2', form.fields)
    
    def test_form_valid_data(self):
        """Form test with valid data"""
        form = AdminAgentCreateForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
    
    def test_form_organisation_field(self):
        """Organisation alanı testi"""
        form = AdminAgentCreateForm()
        
        # Organisation field'ı doğru queryset'e sahip mi
        self.assertIn(self.organisor_profile, form.fields['organisation'].queryset)
        
        # Empty label kontrol et
        self.assertEqual(form.fields['organisation'].empty_label, "Select Organisation")
    
    def test_form_organisation_queryset(self):
        """Organisation queryset testi"""
        form = AdminAgentCreateForm()
        
        # Sadece organisor'ların organisation'ları olmalı
        queryset = form.fields['organisation'].queryset
        for profile in queryset:
            self.assertTrue(profile.user.is_organisor)
            self.assertFalse(profile.user.is_superuser)
    
    def test_form_required_fields(self):
        """Zorunlu alanlar testi"""
        # AdminAgentCreateForm'da sadece email, phone_number, organisation, password1, password2 required
        required_fields = ['email', 'organisation', 'password1', 'password2']
        
        for field in required_fields:
            data = self.valid_data.copy()
            del data[field]
            
            form = AdminAgentCreateForm(data=data)
            self.assertFalse(form.is_valid())
            self.assertIn(field, form.errors)
        
        # Phone number için özel kontrol
        data = self.valid_data.copy()
        del data['phone_number_0']
        del data['phone_number_1']
        form = AdminAgentCreateForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('phone_number', form.errors)
    
    def test_form_save_method(self):
        """Form save metodu testi"""
        form = AdminAgentCreateForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
        
        user = form.save()
        
        # Kullanıcı alanları doğru mu
        self.assertEqual(user.username, 'admin_agent_forms')
        self.assertEqual(user.email, 'admin_agent_forms@example.com')
        self.assertEqual(user.first_name, 'Admin')
        self.assertEqual(user.last_name, 'Agent')
        
        # Şifre doğru set edildi mi
        self.assertTrue(user.check_password('testpass123!'))
    
    def test_form_widget_attributes(self):
        """Widget attributes test"""
        form = AdminAgentCreateForm()
        
        # Check CSS classes and placeholder
        self.assertIn('placeholder="Username"', str(form['username'].as_widget()))
        self.assertIn('placeholder="Enter email address"', str(form['email'].as_widget()))
        self.assertIn('placeholder="First Name"', str(form['first_name'].as_widget()))
        self.assertIn('placeholder="Last Name"', str(form['last_name'].as_widget()))
        
        # Organisation widget
        self.assertIn('class="form-control"', str(form['organisation'].as_widget()))


class TestAgentFormIntegration(TestCase):
    """Agent form entegrasyon testleri"""
    
    def setUp(self):
        """Set up test data"""
        # Create organisor
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
    
    def test_agent_create_form_with_existing_data_conflicts(self):
        """Mevcut verilerle çakışma testi"""
        # Önce bir kullanıcı oluştur
        User.objects.create_user(
            username='conflict_user',
            email='conflict@example.com',
            password='testpass123',
            phone_number='+905551111111'
        )
        
        # Çakışan email ile form test et
        data = {
            'username': 'new_agent',
            'email': 'conflict@example.com',
            'first_name': 'New',
            'last_name': 'Agent',
            'phone_number_0': '+90',
            'phone_number_1': '5552222222',
            'date_of_birth': '1990-01-01',
            'gender': 'M',
            'password1': 'testpass123!',
            'password2': 'testpass123!'
        }
        
        form = AgentCreateForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        
        # Çakışan telefon numarası ile form test et
        data = {
            'username': 'new_agent2',
            'email': 'new_agent2@example.com',
            'first_name': 'New',
            'last_name': 'Agent',
            'phone_number_0': '+90',
            'phone_number_1': '5551111111',
            'date_of_birth': '1990-01-01',
            'gender': 'M',
            'password1': 'testpass123!',
            'password2': 'testpass123!'
        }
        
        form = AgentCreateForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('phone_number', form.errors)
        
        # Çakışan kullanıcı adı ile form test et
        data = {
            'username': 'conflict_user',
            'email': 'new_agent3@example.com',
            'first_name': 'New',
            'last_name': 'Agent',
            'phone_number_0': '+90',
            'phone_number_1': '5553333333',
            'date_of_birth': '1990-01-01',
            'gender': 'M',
            'password1': 'testpass123!',
            'password2': 'testpass123!'
        }
        
        form = AgentCreateForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
    
    def test_admin_agent_create_form_with_organisation(self):
        """Organisation ile admin agent create form testi"""
        data = {
            'username': 'admin_agent',
            'email': 'admin_agent@example.com',
            'first_name': 'Admin',
            'last_name': 'Agent',
            'phone_number_0': '+90',
            'phone_number_1': '5554444444',
            'date_of_birth': '1990-01-01',
            'gender': 'M',
            'organisation': self.organisor_profile.id,
            'password1': 'testpass123!',
            'password2': 'testpass123!'
        }
        
        form = AdminAgentCreateForm(data=data)
        self.assertTrue(form.is_valid())
        
        user = form.save()
        
        # Kullanıcı oluşturuldu mu
        self.assertTrue(User.objects.filter(username='admin_agent').exists())
        
        # Create agent
        agent = Agent.objects.create(user=user, organisation=self.organisor_profile)
        
        # Agent doğru organisation'a atandı mı
        self.assertEqual(agent.organisation, self.organisor_profile)
    
    def test_form_validation_with_empty_data(self):
        """Boş veri ile form validasyon testi"""
        form = AgentCreateForm(data={})
        
        self.assertFalse(form.is_valid())
        # Sadece gerçekten required olan alanları kontrol et
        required_fields = ['email', 'password1', 'password2']
        for field in required_fields:
            self.assertIn(field, form.errors)
    
    def test_form_validation_with_partial_data(self):
        """Kısmi veri ile form validasyon testi"""
        # Sadece username
        form = AgentCreateForm(data={
            'username': 'partial_agent'
        })
        self.assertFalse(form.is_valid())
        # Sadece gerçekten required olan alanları kontrol et
        required_fields = ['email', 'password1', 'password2']
        for field in required_fields:
            self.assertIn(field, form.errors)


if __name__ == "__main__":
    print("Agent Forms Tests Starting...")
    print("=" * 60)
    
    # Run tests
    import unittest
    unittest.main()
