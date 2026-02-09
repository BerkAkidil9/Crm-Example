"""
Finance Integration Test Dosyası
Bu dosya Finance modülünün diğer modüllerle entegrasyonunu test eder.
"""

import os
import sys
import django
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse
from django.db import IntegrityError
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djcrm.settings')
django.setup()

from finance.models import OrderFinanceReport
from finance.views import FinancialReportView
from finance.forms import DateRangeForm
from orders.models import orders, OrderProduct
from leads.models import User, UserProfile, Lead
from ProductsAndStock.models import ProductsAndStock, Category, SubCategory, StockMovement

User = get_user_model()


class TestFinanceOrdersIntegration(TestCase):
    """Finance-Orders entegrasyon testleri"""
    
    def setUp(self):
        """Set up test data"""
        # Organisor kullanıcısı oluştur
        self.organisor_user = User.objects.create_user(
            username='finance_orders_integration',
            email='finance_orders_integration@example.com',
            password='testpass123',
            first_name='Finance',
            last_name='Orders',
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
        
        # Kategori ve ürünler oluştur
        self.category = Category.objects.create(name="Electronics")
        self.subcategory = SubCategory.objects.create(
            name="Smartphones",
            category=self.category
        )
        
        self.product1 = ProductsAndStock.objects.create(
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
        
        self.product2 = ProductsAndStock.objects.create(
            product_name="Samsung Galaxy",
            product_description="Latest Samsung model",
            product_price=899.99,
            cost_price=700.00,
            product_quantity=30,
            minimum_stock_level=5,
            category=self.category,
            subcategory=self.subcategory,
            organisation=self.organisor_profile
        )
    
    def test_order_creation_with_finance_report(self):
        """Order oluşturma ile finance report entegrasyonu"""
        # Order oluştur
        order = orders.objects.create(
            order_day=timezone.now(),
            order_name='Integration Test Order',
            order_description='Order for integration testing',
            organisation=self.organisor_profile,
            lead=self.lead
        )
        
        # OrderProduct'lar oluştur
        order_product1 = OrderProduct.objects.create(
            order=order,
            product=self.product1,
            product_quantity=2
        )
        
        order_product2 = OrderProduct.objects.create(
            order=order,
            product=self.product2,
            product_quantity=3
        )
        
        # Toplam kazanç hesapla
        total_earned = order_product1.total_price + order_product2.total_price
        
        # Finance report oluştur
        finance_report = OrderFinanceReport.objects.create(
            order=order,
            earned_amount=total_earned
        )
        
        # Entegrasyon doğrulaması
        self.assertEqual(finance_report.order, order)
        self.assertEqual(finance_report.earned_amount, total_earned)
        self.assertEqual(order.orderfinancereport, finance_report)
        
        # Order'dan products'a erişim
        self.assertEqual(order.products.count(), 2)
        self.assertIn(self.product1, order.products.all())
        self.assertIn(self.product2, order.products.all())
    
    def test_order_cancellation_finance_report_impact(self):
        """Order iptal etme finance report etkisi"""
        # Order oluştur
        order = orders.objects.create(
            order_day=timezone.now(),
            order_name='Cancellation Test Order',
            order_description='Order for cancellation testing',
            organisation=self.organisor_profile,
            lead=self.lead
        )
        
        # OrderProduct oluştur
        order_product = OrderProduct.objects.create(
            order=order,
            product=self.product1,
            product_quantity=5
        )
        
        # Finance report oluştur
        finance_report = OrderFinanceReport.objects.create(
            order=order,
            earned_amount=order_product.total_price
        )
        
        # Order'ı iptal et
        order.is_cancelled = True
        order.save()
        
        # Finance report hala mevcut olmalı (iptal edilmiş order'lar için de rapor tutulabilir)
        self.assertTrue(OrderFinanceReport.objects.filter(id=finance_report.id).exists())
        self.assertEqual(order.orderfinancereport, finance_report)
    
    def test_order_deletion_finance_report_cascade(self):
        """Order silme finance report cascade testi"""
        # Order oluştur
        order = orders.objects.create(
            order_day=timezone.now(),
            order_name='Deletion Test Order',
            order_description='Order for deletion testing',
            organisation=self.organisor_profile,
            lead=self.lead
        )
        
        # Finance report oluştur
        finance_report = OrderFinanceReport.objects.create(
            order=order,
            earned_amount=1000.0
        )
        
        finance_report_id = finance_report.id
        
        # Order'ı sil
        order.delete()
        
        # Finance report da silinmeli (CASCADE)
        self.assertFalse(OrderFinanceReport.objects.filter(id=finance_report_id).exists())
    
    def test_multiple_orders_finance_reports_aggregation(self):
        """Birden fazla order finance report toplamı"""
        orders_list = []
        total_expected_earned = 0
        
        # Birden fazla order oluştur
        for i in range(3):
            order = orders.objects.create(
                order_day=timezone.now(),
                order_name=f'Order {i+1}',
                order_description=f'Order {i+1} description',
                organisation=self.organisor_profile,
                lead=self.lead
            )
            orders_list.append(order)
            
            # Her order için farklı ürün ve miktar
            product = self.product1 if i % 2 == 0 else self.product2
            quantity = (i + 1) * 2
            
            order_product = OrderProduct.objects.create(
                order=order,
                product=product,
                product_quantity=quantity
            )
            
            # Finance report oluştur
            earned_amount = order_product.total_price
            total_expected_earned += earned_amount
            
            OrderFinanceReport.objects.create(
                order=order,
                earned_amount=earned_amount
            )
        
        # Toplam kazanç hesapla
        from django.db.models import Sum
        total_earned = OrderFinanceReport.objects.aggregate(
            total=Sum('earned_amount')
        )['total']
        
        self.assertEqual(total_earned, total_expected_earned)
        self.assertEqual(OrderFinanceReport.objects.count(), 3)
    
    def test_finance_report_date_filtering_with_orders(self):
        """Finance report tarih filtreleme order'larla entegrasyonu"""
        # Farklı tarihlerde order'lar oluştur - günün başlangıcına sabitle
        from datetime import datetime
        now = timezone.now()
        yesterday = timezone.make_aware(datetime.combine(
            (now - timedelta(days=1)).date(), datetime.min.time()
        ))
        today = timezone.make_aware(datetime.combine(
            now.date(), datetime.min.time()
        ))
        tomorrow = timezone.make_aware(datetime.combine(
            (now + timedelta(days=1)).date(), datetime.min.time()
        ))
        
        dates_and_orders = [
            (yesterday, 'Yesterday Order'),
            (today, 'Today Order'),
            (tomorrow, 'Tomorrow Order')
        ]
        
        for order_date, order_name in dates_and_orders:
            order = orders.objects.create(
                order_day=order_date,
                order_name=order_name,
                order_description=f'{order_name} description',
                organisation=self.organisor_profile,
                lead=self.lead,
                creation_date=order_date  # creation_date manuel set et
            )
            
            OrderFinanceReport.objects.create(
                order=order,
                earned_amount=1000.0
            )
        
        # Bugünkü order'ları filtrele
        today_reports = OrderFinanceReport.objects.filter(
            order__creation_date__date=today.date()
        )
        
        self.assertEqual(today_reports.count(), 1)  # Sadece bugünkü order
        self.assertIn('Today Order', [report.order.order_name for report in today_reports])
    
    def test_finance_report_organisation_filtering(self):
        """Finance report organizasyon filtreleme"""
        # Farklı organizasyon oluştur
        org2_user = User.objects.create_user(
            username='org2_finance_integration',
            email='org2_finance_integration@example.com',
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
        
        # Her organizasyon için order ve finance report oluştur
        order1 = orders.objects.create(
            order_day=timezone.now(),
            order_name='Org1 Order',
            order_description='Order for org1',
            organisation=self.organisor_profile,
            lead=self.lead
        )
        
        order2 = orders.objects.create(
            order_day=timezone.now(),
            order_name='Org2 Order',
            order_description='Order for org2',
            organisation=org2_profile,
            lead=self.lead
        )
        
        finance_report1 = OrderFinanceReport.objects.create(
            order=order1,
            earned_amount=1000.0
        )
        
        finance_report2 = OrderFinanceReport.objects.create(
            order=order2,
            earned_amount=2000.0
        )
        
        # Sadece org1'in finance report'larını filtrele
        org1_reports = OrderFinanceReport.objects.filter(
            order__organisation=self.organisor_profile
        )
        
        self.assertEqual(org1_reports.count(), 1)
        self.assertEqual(org1_reports.first(), finance_report1)
        
        # Sadece org2'nin finance report'larını filtrele
        org2_reports = OrderFinanceReport.objects.filter(
            order__organisation=org2_profile
        )
        
        self.assertEqual(org2_reports.count(), 1)
        self.assertEqual(org2_reports.first(), finance_report2)


class TestFinanceProductsIntegration(TestCase):
    """Finance-Products entegrasyon testleri"""
    
    def setUp(self):
        """Set up test data"""
        # Organisor kullanıcısı oluştur
        self.organisor_user = User.objects.create_user(
            username='finance_products_integration',
            email='finance_products_integration@example.com',
            password='testpass123',
            first_name='Finance',
            last_name='Products',
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
        
        # Kategori ve ürünler oluştur
        self.category = Category.objects.create(name="Electronics")
        self.subcategory = SubCategory.objects.create(
            name="Smartphones",
            category=self.category
        )
        
        self.product1 = ProductsAndStock.objects.create(
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
        
        self.product2 = ProductsAndStock.objects.create(
            product_name="Samsung Galaxy",
            product_description="Latest Samsung model",
            product_price=899.99,
            cost_price=700.00,
            product_quantity=30,
            minimum_stock_level=5,
            category=self.category,
            subcategory=self.subcategory,
            organisation=self.organisor_profile
        )
    
    def test_finance_report_product_profit_calculation(self):
        """Finance report ürün kar hesaplama entegrasyonu"""
        # Order oluştur
        order = orders.objects.create(
            order_day=timezone.now(),
            order_name='Profit Calculation Order',
            order_description='Order for profit calculation',
            organisation=self.organisor_profile,
            lead=self.lead
        )
        
        # OrderProduct oluştur
        order_product = OrderProduct.objects.create(
            order=order,
            product=self.product1,
            product_quantity=2
        )
        
        # Finance report oluştur
        finance_report = OrderFinanceReport.objects.create(
            order=order,
            earned_amount=order_product.total_price
        )
        
        # Kar hesaplama
        total_revenue = order_product.total_price
        total_cost = order_product.product_quantity * order_product.product.cost_price
        profit = total_revenue - total_cost
        
        # Kar hesaplaması doğrulaması
        expected_profit = 2 * (self.product1.product_price - self.product1.cost_price)
        self.assertEqual(profit, expected_profit)
        self.assertEqual(finance_report.earned_amount, total_revenue)
    
    def test_finance_report_multiple_products_profit(self):
        """Finance report birden fazla ürün kar hesaplama"""
        # Order oluştur
        order = orders.objects.create(
            order_day=timezone.now(),
            order_name='Multiple Products Order',
            order_description='Order with multiple products',
            organisation=self.organisor_profile,
            lead=self.lead
        )
        
        # Birden fazla OrderProduct oluştur
        order_product1 = OrderProduct.objects.create(
            order=order,
            product=self.product1,
            product_quantity=2
        )
        
        order_product2 = OrderProduct.objects.create(
            order=order,
            product=self.product2,
            product_quantity=3
        )
        
        # Toplam gelir ve maliyet hesapla
        total_revenue = order_product1.total_price + order_product2.total_price
        total_cost = (order_product1.product_quantity * order_product1.product.cost_price + 
                     order_product2.product_quantity * order_product2.product.cost_price)
        total_profit = total_revenue - total_cost
        
        # Finance report oluştur
        finance_report = OrderFinanceReport.objects.create(
            order=order,
            earned_amount=total_revenue
        )
        
        # Hesaplamaları doğrula
        self.assertEqual(finance_report.earned_amount, total_revenue)
        self.assertGreater(total_profit, 0)  # Kar pozitif olmalı
        
        # Beklenen kar hesaplaması (float precision için almost equal kullan)
        expected_profit = (2 * (self.product1.product_price - self.product1.cost_price) + 
                          3 * (self.product2.product_price - self.product2.cost_price))
        self.assertAlmostEqual(total_profit, expected_profit, places=2)
    
    def test_finance_report_stock_movement_integration(self):
        """Finance report stok hareket entegrasyonu"""
        # Order oluştur
        order = orders.objects.create(
            order_day=timezone.now(),
            order_name='Stock Movement Order',
            order_description='Order for stock movement testing',
            organisation=self.organisor_profile,
            lead=self.lead
        )
        
        # OrderProduct oluştur (stok azaltılacak)
        order_product = OrderProduct.objects.create(
            order=order,
            product=self.product1,
            product_quantity=5
        )
        
        # Finance report oluştur
        finance_report = OrderFinanceReport.objects.create(
            order=order,
            earned_amount=order_product.total_price
        )
        
        # Stok hareketi oluşturulmuş olmalı
        stock_movements = StockMovement.objects.filter(
            product=self.product1,
            movement_type='OUT'
        )
        
        self.assertTrue(stock_movements.exists())
        
        # Stok miktarı azaltılmış olmalı
        self.product1.refresh_from_db()
        expected_stock = 50 - 5  # Initial stock - quantity
        self.assertEqual(self.product1.product_quantity, expected_stock)
        
        # Finance report ile stok hareketi ilişkisi
        self.assertEqual(finance_report.order, order)
        self.assertEqual(order.products.first(), self.product1)


class TestFinanceViewsIntegration(TestCase):
    """Finance Views entegrasyon testleri"""
    
    def setUp(self):
        """Set up test data"""
        # Organisor kullanıcısı oluştur
        self.organisor_user = User.objects.create_user(
            username='finance_views_integration',
            email='finance_views_integration@example.com',
            password='testpass123',
            first_name='Finance',
            last_name='Views',
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
        
        # Tarih değişkenleri
        from datetime import datetime
        now = timezone.now()
        self.today = timezone.make_aware(datetime.combine(
            now.date(), datetime.min.time()
        ))
    
    def test_financial_report_view_full_workflow(self):
        """FinancialReportView tam workflow testi"""
        from django.test import Client
        
        client = Client()
        
        # Order ve finance report oluştur
        order = orders.objects.create(
            order_day=self.today,
            order_name='Full Workflow Order',
            order_description='Order for full workflow testing',
            organisation=self.organisor_profile,
            lead=self.lead,
            creation_date=self.today
        )
        
        order_product = OrderProduct.objects.create(
            order=order,
            product=self.product,
            product_quantity=2
        )
        
        finance_report = OrderFinanceReport.objects.create(
            order=order,
            earned_amount=order_product.total_price
        )
        
        # GET request
        response = client.get(reverse('finance:financial_report'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Financial Report')
        
        # POST request with date range
        today = self.today.date()
        response = client.post(reverse('finance:financial_report'), {
            'start_date': today,
            'end_date': today
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Total Earned: $')
        self.assertContains(response, 'Full Workflow Order')
    
    def test_financial_report_view_form_integration(self):
        """FinancialReportView form entegrasyonu"""
        from django.test import Client
        
        client = Client()
        
        # GET request - form render edilmeli
        response = client.get(reverse('finance:financial_report'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        
        # Form DateRangeForm olmalı
        self.assertIsInstance(response.context['form'], DateRangeForm)
        
        # POST request - form validation
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        
        # Valid form
        response = client.post(reverse('finance:financial_report'), {
            'start_date': today,
            'end_date': today
        })
        self.assertEqual(response.status_code, 200)
        
        # Invalid form (end_date before start_date)
        response = client.post(reverse('finance:financial_report'), {
            'start_date': today,
            'end_date': yesterday
        })
        self.assertEqual(response.status_code, 200)
        # Form hatalı olduğu için GET response döner


class TestFinanceDataConsistency(TransactionTestCase):
    """Finance veri tutarlılığı testleri"""
    
    def setUp(self):
        """Set up test data"""
        # Organisor kullanıcısı oluştur
        self.organisor_user = User.objects.create_user(
            username='finance_consistency',
            email='finance_consistency@example.com',
            password='testpass123',
            first_name='Finance',
            last_name='Consistency',
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
    
    def test_finance_report_data_consistency(self):
        """Finance report veri tutarlılığı testi"""
        # Order oluştur
        order = orders.objects.create(
            order_day=timezone.now(),
            order_name='Consistency Test Order',
            order_description='Order for consistency testing',
            organisation=self.organisor_profile,
            lead=self.lead
        )
        
        # OrderProduct oluştur
        order_product = OrderProduct.objects.create(
            order=order,
            product=self.product,
            product_quantity=3
        )
        
        # Finance report oluştur
        finance_report = OrderFinanceReport.objects.create(
            order=order,
            earned_amount=order_product.total_price
        )
        
        # Veri tutarlılığı kontrolü
        self.assertEqual(finance_report.order, order)
        self.assertEqual(finance_report.earned_amount, order_product.total_price)
        self.assertEqual(order.orderfinancereport, finance_report)
        
        # Order'dan products'a erişim
        self.assertEqual(order.products.count(), 1)
        self.assertEqual(order.products.first(), self.product)
        
        # OrderProduct'dan order'a erişim
        self.assertEqual(order_product.order, order)
        self.assertEqual(order_product.product, self.product)
    
    def test_finance_report_unique_constraint(self):
        """Finance report unique constraint testi"""
        # Order oluştur
        order = orders.objects.create(
            order_day=timezone.now(),
            order_name='Unique Constraint Order',
            order_description='Order for unique constraint testing',
            organisation=self.organisor_profile,
            lead=self.lead
        )
        
        # İlk finance report oluştur
        finance_report1 = OrderFinanceReport.objects.create(
            order=order,
            earned_amount=1000.0
        )
        
        # Aynı order ile ikinci finance report oluşturmaya çalış
        with self.assertRaises(IntegrityError):
            OrderFinanceReport.objects.create(
                order=order,
                earned_amount=2000.0
            )
        
        # TransactionTestCase kullandığımız için rollback olmaz
        # Sadece bir finance report olmalı
        self.assertEqual(OrderFinanceReport.objects.filter(order=order).count(), 1)
        self.assertEqual(OrderFinanceReport.objects.get(order=order), finance_report1)


if __name__ == "__main__":
    print("Finance Integration Testleri Başlatılıyor...")
    print("=" * 60)
    
    # Test çalıştırma
    import unittest
    unittest.main()
