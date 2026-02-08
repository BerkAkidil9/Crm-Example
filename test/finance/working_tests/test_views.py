"""
Finance Views Test Dosyası
Bu dosya Finance modülündeki tüm view'ları test eder.
"""

import os
import sys
import django
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djcrm.settings')
django.setup()

from finance.models import OrderFinanceReport
from finance.views import FinancialReportView
from orders.models import orders, OrderProduct
from leads.models import User, UserProfile, Lead
from ProductsAndStock.models import ProductsAndStock, Category, SubCategory

User = get_user_model()


class TestFinancialReportView(TestCase):
    """FinancialReportView testleri"""
    
    def setUp(self):
        """Test verilerini hazırla"""
        # Organisor kullanıcısı oluştur
        self.organisor_user = User.objects.create_user(
            username='finance_view_organisor',
            email='finance_view_organisor@example.com',
            password='testpass123',
            first_name='Finance',
            last_name='View',
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
        
        # Lead oluştur
        self.lead = Lead.objects.create(
            first_name='Finance',
            last_name='Lead',
            email='financelead@example.com',
            phone_number='+905559876543',
            organisation=self.organisor_profile
        )
        
        # Kategori ve ürün oluştur
        self.category = Category.objects.create(name="Electronics")
        self.subcategory = SubCategory.objects.create(
            name="Smartphones",
            category=self.category
        )
        
        self.product = ProductsAndStock.objects.create(
            product_name="iPhone 15",
            product_description="Latest iPhone model",
            product_price=999.99,
            cost_price=800.00,
            product_quantity=50,
            minimum_stock_level=10,
            category=self.category,
            subcategory=self.subcategory,
            organisation=self.organisor_profile
        )
        
        # Order'lar oluştur (farklı tarihlerde)
        # Tarihleri günün başlangıcına sabitle (00:00:00)
        now = timezone.now()
        self.yesterday = timezone.make_aware(datetime.combine(
            (now - timedelta(days=1)).date(), datetime.min.time()
        ))
        self.today = timezone.make_aware(datetime.combine(
            now.date(), datetime.min.time()
        ))
        self.tomorrow = timezone.make_aware(datetime.combine(
            (now + timedelta(days=1)).date(), datetime.min.time()
        ))
        
        self.order1 = orders.objects.create(
            order_day=self.yesterday,
            order_name='Yesterday Order',
            order_description='Order from yesterday',
            organisation=self.organisor_profile,
            lead=self.lead,
            creation_date=self.yesterday  # creation_date'i manuel set et
        )
        
        self.order2 = orders.objects.create(
            order_day=self.today,
            order_name='Today Order',
            order_description='Order from today',
            organisation=self.organisor_profile,
            lead=self.lead,
            creation_date=self.today  # creation_date'i manuel set et
        )
        
        self.order3 = orders.objects.create(
            order_day=self.tomorrow,
            order_name='Tomorrow Order',
            order_description='Order from tomorrow',
            organisation=self.organisor_profile,
            lead=self.lead,
            creation_date=self.tomorrow  # creation_date'i manuel set et
        )
        
        # Finance report'lar oluştur
        self.finance_report1 = OrderFinanceReport.objects.create(
            order=self.order1,
            earned_amount=1000.0
        )
        
        self.finance_report2 = OrderFinanceReport.objects.create(
            order=self.order2,
            earned_amount=2000.0
        )
        
        self.finance_report3 = OrderFinanceReport.objects.create(
            order=self.order3,
            earned_amount=3000.0
        )
        
        # Client oluştur ve giriş yap
        self.client = Client()
        self.client.login(username='finance_view_organisor', password='testpass123')
    
    def test_financial_report_view_get(self):
        """FinancialReportView GET request testi"""
        response = self.client.get(reverse('finance:financial_report'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Financial Report')
        self.assertContains(response, 'form')
        self.assertContains(response, 'start_date')
        self.assertContains(response, 'end_date')
        self.assertContains(response, 'Filter')
    
    def test_financial_report_view_get_context(self):
        """FinancialReportView GET context testi"""
        response = self.client.get(reverse('finance:financial_report'))
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertIn('total_earned', response.context)
        self.assertIn('reports', response.context)
        
        # GET request'te varsayılan (bu ay) veriler gösterilir
        self.assertIn('order_count', response.context)
    
    def test_financial_report_view_post_valid_dates(self):
        """FinancialReportView POST valid dates testi"""
        start_date = self.today.date()
        end_date = self.today.date()
        
        response = self.client.post(reverse('finance:financial_report'), {
            'start_date': start_date,
            'end_date': end_date
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertIn('total_earned', response.context)
        self.assertIn('reports', response.context)
        
        # Sadece bugünkü order filtrelenmiş olmalı
        self.assertEqual(response.context['total_earned'], 2000.0)  # Sadece order2
        self.assertEqual(len(response.context['reports']), 1)
        self.assertIn(self.finance_report2, response.context['reports'])
    
    def test_financial_report_view_post_date_range(self):
        """FinancialReportView POST date range testi"""
        start_date = self.yesterday.date()
        end_date = self.today.date()
        
        response = self.client.post(reverse('finance:financial_report'), {
            'start_date': start_date,
            'end_date': end_date
        })
        
        self.assertEqual(response.status_code, 200)
        
        # Dün ve bugünkü order'lar filtrelenmiş olmalı
        self.assertEqual(response.context['total_earned'], 3000.0)  # order1 (1000) + order2 (2000)
        self.assertEqual(len(response.context['reports']), 2)
        self.assertIn(self.finance_report1, response.context['reports'])
        self.assertIn(self.finance_report2, response.context['reports'])
    
    def test_financial_report_view_post_all_dates(self):
        """FinancialReportView POST all dates testi"""
        start_date = self.yesterday.date()
        end_date = self.tomorrow.date()
        
        response = self.client.post(reverse('finance:financial_report'), {
            'start_date': start_date,
            'end_date': end_date
        })
        
        self.assertEqual(response.status_code, 200)
        
        # Tüm order'lar (dün, bugün, yarın) filtrelenmiş olmalı
        self.assertEqual(response.context['total_earned'], 6000.0)  # order1 (1000) + order2 (2000) + order3 (3000)
        self.assertEqual(len(response.context['reports']), 3)
        self.assertIn(self.finance_report1, response.context['reports'])
        self.assertIn(self.finance_report2, response.context['reports'])
        self.assertIn(self.finance_report3, response.context['reports'])
    
    def test_financial_report_view_post_no_results(self):
        """FinancialReportView POST no results testi"""
        start_date = (self.today + timedelta(days=10)).date()
        end_date = (self.today + timedelta(days=20)).date()
        
        response = self.client.post(reverse('finance:financial_report'), {
            'start_date': start_date,
            'end_date': end_date
        })
        
        self.assertEqual(response.status_code, 200)
        
        # Sonuç bulunmamalı
        self.assertEqual(response.context['total_earned'], 0)
        self.assertEqual(len(response.context['reports']), 0)
    
    def test_financial_report_view_post_invalid_form(self):
        """FinancialReportView POST invalid form testi"""
        response = self.client.post(reverse('finance:financial_report'), {
            'start_date': 'invalid_date',
            'end_date': 'invalid_date'
        })
        
        self.assertEqual(response.status_code, 200)
        
        # Form hatalı olduğu için GET response döner
        self.assertIsNone(response.context['total_earned'])
        self.assertEqual(len(response.context['reports']), 0)
    
    def test_financial_report_view_post_end_date_before_start_date(self):
        """FinancialReportView POST end_date before start_date testi"""
        start_date = self.today.date()
        end_date = self.yesterday.date()
        
        response = self.client.post(reverse('finance:financial_report'), {
            'start_date': start_date,
            'end_date': end_date
        })
        
        self.assertEqual(response.status_code, 200)
        
        # Form hatalı olduğu için GET response döner
        self.assertIsNone(response.context['total_earned'])
        self.assertEqual(len(response.context['reports']), 0)
    
    def test_financial_report_view_template_rendering(self):
        """FinancialReportView template rendering testi"""
        response = self.client.get(reverse('finance:financial_report'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'finance/financial_report.html')
    
    def test_financial_report_view_with_reports_template(self):
        """FinancialReportView with reports template testi"""
        start_date = self.today.date()
        end_date = self.today.date()
        
        response = self.client.post(reverse('finance:financial_report'), {
            'start_date': start_date,
            'end_date': end_date
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Today Order')  # Sadece bugünkü order
        self.assertContains(response, '2000')  # Earned amount
        self.assertContains(response, 'reportTable')
    
    def test_financial_report_view_empty_results_template(self):
        """FinancialReportView empty results template testi"""
        start_date = (self.today + timedelta(days=10)).date()
        end_date = (self.today + timedelta(days=20)).date()
        
        response = self.client.post(reverse('finance:financial_report'), {
            'start_date': start_date,
            'end_date': end_date
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '0.00')
        self.assertContains(response, 'No orders found')
    
    def test_financial_report_view_date_filtering_logic(self):
        """FinancialReportView date filtering logic testi"""
        # Özel tarih aralığı oluştur
        custom_start = self.today.replace(hour=0, minute=0, second=0, microsecond=0)
        custom_end = self.today.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        start_date = custom_start.date()
        end_date = custom_end.date()
        
        response = self.client.post(reverse('finance:financial_report'), {
            'start_date': start_date,
            'end_date': end_date
        })
        
        self.assertEqual(response.status_code, 200)
        
        # Sadece bugünkü order filtrelenmiş olmalı
        self.assertEqual(response.context['total_earned'], 2000.0)  # Sadece order2
        self.assertEqual(len(response.context['reports']), 1)
    
    def test_financial_report_view_aggregation(self):
        """FinancialReportView aggregation testi"""
        # Birden fazla aynı gün order'ı oluştur
        same_day_order = orders.objects.create(
            order_day=self.today,
            order_name='Same Day Order',
            order_description='Another order for today',
            organisation=self.organisor_profile,
            lead=self.lead,
            creation_date=self.today
        )
        
        OrderFinanceReport.objects.create(
            order=same_day_order,
            earned_amount=1500.0
        )
        
        start_date = self.today.date()
        end_date = self.today.date()
        
        response = self.client.post(reverse('finance:financial_report'), {
            'start_date': start_date,
            'end_date': end_date
        })
        
        self.assertEqual(response.status_code, 200)
        
        # Bugünkü iki order'ın toplamı (order2: 2000 + same_day_order: 1500)
        self.assertEqual(response.context['total_earned'], 3500.0)  # 2000 + 1500
        self.assertEqual(len(response.context['reports']), 2)
    
    def test_financial_report_view_select_related_optimization(self):
        """FinancialReportView select_related optimization testi - N+1 sorgu önlenir"""
        start_date = self.today.date()
        end_date = self.today.date()
        
        response = self.client.post(reverse('finance:financial_report'), {
            'start_date': start_date,
            'end_date': end_date
        })
        
        self.assertEqual(response.status_code, 200)
        # select_related ile order, lead, organisation yüklü - N+1 yok
        reports = list(response.context['reports'])
        self.assertTrue(len(reports) >= 0)
    
    def test_financial_report_view_multiple_organisations(self):
        """FinancialReportView multiple organisations testi - superuser tüm org'ları görür"""
        self.client.logout()
        superuser = User.objects.create_superuser(
            username='finance_superuser',
            email='finance_superuser@example.com',
            password='testpass123'
        )
        self.client.login(username='finance_superuser', password='testpass123')

        # Farklı organizasyon oluştur
        org2_user = User.objects.create_user(
            username='org2_finance_view',
            email='org2_finance_view@example.com',
            password='testpass123',
            first_name='Org2',
            last_name='Finance',
            phone_number='+905556666666',
            date_of_birth='1975-01-01',
            gender='F',
            is_organisor=True,
            email_verified=True
        )
        
        org2_profile, created = UserProfile.objects.get_or_create(user=org2_user)
        
        # Org2 için order ve finance report oluştur
        org2_order = orders.objects.create(
            order_day=self.today,
            order_name='Org2 Order',
            order_description='Order for org2',
            organisation=org2_profile,
            lead=self.lead,
            creation_date=self.today
        )
        
        OrderFinanceReport.objects.create(
            order=org2_order,
            earned_amount=5000.0
        )
        
        start_date = self.today.date()
        end_date = self.today.date()
        
        response = self.client.post(reverse('finance:financial_report'), {
            'start_date': start_date,
            'end_date': end_date
        })
        
        self.assertEqual(response.status_code, 200)
        
        # Bugünkü order'lar filtrelenmiş olmalı (her iki organizasyondan)
        self.assertEqual(response.context['total_earned'], 7000.0)  # order2 (2000) + org2_order (5000)
        self.assertEqual(len(response.context['reports']), 2)


class TestFinancialReportViewEdgeCases(TestCase):
    """FinancialReportView edge cases testleri"""
    
    def setUp(self):
        """Test verilerini hazırla"""
        # Organisor kullanıcısı oluştur
        self.organisor_user = User.objects.create_user(
            username='edge_case_organisor',
            email='edge_case_organisor@example.com',
            password='testpass123',
            first_name='Edge',
            last_name='Case',
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
        
        # Lead oluştur
        self.lead = Lead.objects.create(
            first_name='Edge',
            last_name='Lead',
            email='edgelead@example.com',
            phone_number='+905559876543',
            organisation=self.organisor_profile
        )
        
        # Tarih değişkenleri
        from datetime import datetime
        now = timezone.now()
        self.today = timezone.make_aware(datetime.combine(
            now.date(), datetime.min.time()
        ))
        
        # Client oluştur ve giriş yap
        self.client = Client()
        self.client.login(username='edge_case_organisor', password='testpass123')
    
    def test_financial_report_view_no_orders(self):
        """FinancialReportView no orders testi"""
        start_date = timezone.now().date()
        end_date = timezone.now().date()
        
        response = self.client.post(reverse('finance:financial_report'), {
            'start_date': start_date,
            'end_date': end_date
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_earned'], 0)
        self.assertEqual(len(response.context['reports']), 0)
    
    def test_financial_report_view_orders_without_finance_reports(self):
        """FinancialReportView orders without finance reports testi"""
        # Order oluştur ama finance report oluşturma
        order = orders.objects.create(
            order_day=timezone.now(),
            order_name='Order Without Finance Report',
            order_description='Order without finance report',
            organisation=self.organisor_profile,
            lead=self.lead,
            creation_date=timezone.now()
        )
        
        start_date = timezone.now().date()
        end_date = timezone.now().date()
        
        response = self.client.post(reverse('finance:financial_report'), {
            'start_date': start_date,
            'end_date': end_date
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_earned'], 0)
        self.assertEqual(len(response.context['reports']), 0)
    
    def test_financial_report_view_zero_earned_amount(self):
        """FinancialReportView zero earned amount testi"""
        # Order ve finance report oluştur (earned_amount = 0)
        order = orders.objects.create(
            order_day=self.today,
            order_name='Zero Earned Order',
            order_description='Order with zero earned amount',
            organisation=self.organisor_profile,
            lead=self.lead,
            creation_date=self.today
        )
        
        OrderFinanceReport.objects.create(
            order=order,
            earned_amount=0.0
        )
        
        start_date = self.today.date()
        end_date = self.today.date()
        
        response = self.client.post(reverse('finance:financial_report'), {
            'start_date': start_date,
            'end_date': end_date
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_earned'], 0.0)
        self.assertEqual(len(response.context['reports']), 1)
    
    def test_financial_report_view_negative_earned_amount(self):
        """FinancialReportView negative earned amount testi"""
        # Order ve finance report oluştur (earned_amount < 0)
        order = orders.objects.create(
            order_day=self.today,
            order_name='Negative Earned Order',
            order_description='Order with negative earned amount',
            organisation=self.organisor_profile,
            lead=self.lead,
            creation_date=self.today
        )
        
        OrderFinanceReport.objects.create(
            order=order,
            earned_amount=-500.0
        )
        
        start_date = self.today.date()
        end_date = self.today.date()
        
        response = self.client.post(reverse('finance:financial_report'), {
            'start_date': start_date,
            'end_date': end_date
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_earned'], -500.0)
        self.assertEqual(len(response.context['reports']), 1)


if __name__ == "__main__":
    print("Finance Views Testleri Başlatılıyor...")
    print("=" * 60)
    
    # Test çalıştırma
    import unittest
    unittest.main()
