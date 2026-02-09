"""
Finance Models Test File
This file tests all models in the Finance module.
"""

import os
import sys
import django
from django.test import TestCase, TransactionTestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import IntegrityError
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

# Load Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djcrm.settings')
django.setup()

from finance.models import OrderFinanceReport
from orders.models import orders, OrderProduct
from leads.models import User, UserProfile, Lead
from ProductsAndStock.models import ProductsAndStock, Category, SubCategory


class TestOrderFinanceReportModel(TestCase):
    """OrderFinanceReport model tests"""
    
    def setUp(self):
        """Set up test data"""
        # Create organisor user
        self.organisor_user = User.objects.create_user(
            username='finance_organisor_test',
            email='finance_organisor_test@example.com',
            password='testpass123',
            first_name='Finance',
            last_name='Organisor',
            phone_number='+905551234567',
            date_of_birth='1980-01-01',
            gender='M',
            is_organisor=True,
            email_verified=True
        )
        
        # Create UserProfile
        self.organisor_profile, created = UserProfile.objects.get_or_create(
            user=self.organisor_user
        )
        
        # Create Lead
        self.lead = Lead.objects.create(
            first_name='Finance',
            last_name='Lead',
            email='financelead@example.com',
            phone_number='+905559876543',
            organisation=self.organisor_profile
        )
        
        # Create category and product
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
        
        # Create Order
        self.order = orders.objects.create(
            order_day=timezone.now(),
            order_name='Finance Test Order',
            order_description='Order for finance testing',
            organisation=self.organisor_profile,
            lead=self.lead
        )
    
    def test_order_finance_report_creation(self):
        """OrderFinanceReport oluşturma testi"""
        finance_report = OrderFinanceReport.objects.create(
            order=self.order,
            earned_amount=1999.98
        )
        
        self.assertEqual(finance_report.order, self.order)
        self.assertEqual(finance_report.earned_amount, 1999.98)
        self.assertIsNotNone(finance_report.report_date)
    
    def test_order_finance_report_str_representation(self):
        """OrderFinanceReport __str__ metodu testi"""
        finance_report = OrderFinanceReport.objects.create(
            order=self.order,
            earned_amount=1999.98
        )
        
        expected_str = f"Report for {self.order.order_name} - {finance_report.report_date.strftime('%Y-%m-%d')}"
        self.assertEqual(str(finance_report), expected_str)
    
    def test_order_finance_report_default_report_date(self):
        """OrderFinanceReport default report_date testi"""
        finance_report = OrderFinanceReport.objects.create(
            order=self.order,
            earned_amount=1999.98
        )
        
        # Report date otomatik ayarlanmış olmalı
        self.assertIsNotNone(finance_report.report_date)
        
        # Şimdiki zamandan fazla fark etmemeli
        time_diff = timezone.now() - finance_report.report_date
        self.assertLess(time_diff.total_seconds(), 5)
    
    def test_order_finance_report_manual_report_date(self):
        """OrderFinanceReport manuel report_date testi"""
        custom_date = timezone.now() - timedelta(days=1)
        
        finance_report = OrderFinanceReport.objects.create(
            order=self.order,
            earned_amount=1999.98,
            report_date=custom_date
        )
        
        self.assertEqual(finance_report.report_date, custom_date)
    
    def test_order_finance_report_earned_amount_positive(self):
        """OrderFinanceReport earned_amount pozitif değer testi"""
        finance_report = OrderFinanceReport.objects.create(
            order=self.order,
            earned_amount=100.50
        )
        
        self.assertEqual(finance_report.earned_amount, 100.50)
    
    def test_order_finance_report_earned_amount_zero(self):
        """OrderFinanceReport earned_amount sıfır değeri testi"""
        finance_report = OrderFinanceReport.objects.create(
            order=self.order,
            earned_amount=0.0
        )
        
        self.assertEqual(finance_report.earned_amount, 0.0)
    
    def test_order_finance_report_earned_amount_negative(self):
        """OrderFinanceReport earned_amount negatif değer testi"""
        finance_report = OrderFinanceReport.objects.create(
            order=self.order,
            earned_amount=-50.0
        )
        
        self.assertEqual(finance_report.earned_amount, -50.0)
    
    def test_order_finance_report_one_to_one_relationship(self):
        """OrderFinanceReport OneToOneField ilişkisi testi"""
        finance_report = OrderFinanceReport.objects.create(
            order=self.order,
            earned_amount=1999.98
        )
        
        # OneToOneField testi
        self.assertEqual(finance_report.order, self.order)
        
        # Order'dan finance report'a erişim
        self.assertEqual(self.order.orderfinancereport, finance_report)
    
    def test_order_finance_report_unique_order_constraint(self):
        """OrderFinanceReport unique order constraint testi"""
        # İlk finance report oluştur
        OrderFinanceReport.objects.create(
            order=self.order,
            earned_amount=1999.98
        )
        
        # Aynı order ile ikinci finance report oluşturmaya çalış
        with self.assertRaises(IntegrityError):
            OrderFinanceReport.objects.create(
                order=self.order,
                earned_amount=1500.0
            )
    
    def test_order_finance_report_cascade_delete_order(self):
        """OrderFinanceReport cascade delete order testi"""
        finance_report = OrderFinanceReport.objects.create(
            order=self.order,
            earned_amount=1999.98
        )
        
        finance_report_id = finance_report.id
        order_id = self.order.id
        
        # Delete Order
        self.order.delete()
        
        # Finance report should also be deleted
        self.assertFalse(OrderFinanceReport.objects.filter(id=finance_report_id).exists())
        self.assertFalse(orders.objects.filter(id=order_id).exists())
    
    def test_order_finance_report_float_precision(self):
        """OrderFinanceReport float precision testi"""
        finance_report = OrderFinanceReport.objects.create(
            order=self.order,
            earned_amount=123.456789
        )
        
        # Float değer doğru kaydedilmeli
        self.assertAlmostEqual(finance_report.earned_amount, 123.456789, places=6)
    
    def test_order_finance_report_large_amount(self):
        """OrderFinanceReport büyük miktar testi"""
        large_amount = 999999.99
        
        finance_report = OrderFinanceReport.objects.create(
            order=self.order,
            earned_amount=large_amount
        )
        
        self.assertEqual(finance_report.earned_amount, large_amount)


class TestOrderFinanceReportModelIntegration(TestCase):
    """OrderFinanceReport model entegrasyon testleri"""
    
    def setUp(self):
        """Set up test data"""
        # Create organisor user
        self.organisor_user = User.objects.create_user(
            username='integration_finance_organisor',
            email='integration_finance_organisor@example.com',
            password='testpass123',
            first_name='Integration',
            last_name='Finance',
            phone_number='+905551234567',
            date_of_birth='1980-01-01',
            gender='M',
            is_organisor=True,
            email_verified=True
        )
        
        # Create UserProfile
        self.organisor_profile, created = UserProfile.objects.get_or_create(
            user=self.organisor_user
        )
        
        # Create Lead
        self.lead = Lead.objects.create(
            first_name='Integration',
            last_name='Lead',
            email='integrationlead@example.com',
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
    
    def test_order_finance_report_with_order_products(self):
        """OrderFinanceReport ile OrderProduct entegrasyon testi"""
        # Create Order
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
        
        # Calculate total earned
        total_earned = order_product1.total_price + order_product2.total_price
        
        # Finance report oluştur
        finance_report = OrderFinanceReport.objects.create(
            order=order,
            earned_amount=total_earned
        )
        
        # Doğrulama
        self.assertEqual(finance_report.order, order)
        self.assertEqual(finance_report.earned_amount, total_earned)
        
        # Order'dan finance report'a erişim
        self.assertEqual(order.orderfinancereport, finance_report)
    
    def test_multiple_orders_finance_reports(self):
        """Multiple orders and finance report test"""
        # Create multiple orders
        order1 = orders.objects.create(
            order_day=timezone.now(),
            order_name='Order 1',
            order_description='First order',
            organisation=self.organisor_profile,
            lead=self.lead
        )
        
        order2 = orders.objects.create(
            order_day=timezone.now(),
            order_name='Order 2',
            order_description='Second order',
            organisation=self.organisor_profile,
            lead=self.lead
        )
        
        # Finance report'lar oluştur
        finance_report1 = OrderFinanceReport.objects.create(
            order=order1,
            earned_amount=1000.0
        )
        
        finance_report2 = OrderFinanceReport.objects.create(
            order=order2,
            earned_amount=2000.0
        )
        
        # Her order'ın kendi finance report'ı olmalı
        self.assertEqual(order1.orderfinancereport, finance_report1)
        self.assertEqual(order2.orderfinancereport, finance_report2)
        
        # Finance report'lar farklı olmalı
        self.assertNotEqual(finance_report1, finance_report2)
        self.assertNotEqual(finance_report1.order, finance_report2.order)
    
    def test_order_finance_report_date_filtering(self):
        """OrderFinanceReport tarih filtreleme testi"""
        # Create orders on different dates - fix to start of day
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
        
        order1 = orders.objects.create(
            order_day=yesterday,
            order_name='Yesterday Order',
            order_description='Order from yesterday',
            organisation=self.organisor_profile,
            lead=self.lead,
            creation_date=yesterday
        )
        
        order2 = orders.objects.create(
            order_day=today,
            order_name='Today Order',
            order_description='Order from today',
            organisation=self.organisor_profile,
            lead=self.lead,
            creation_date=today
        )
        
        order3 = orders.objects.create(
            order_day=tomorrow,
            order_name='Tomorrow Order',
            order_description='Order from tomorrow',
            organisation=self.organisor_profile,
            lead=self.lead,
            creation_date=tomorrow
        )
        
        # Finance report'lar oluştur
        finance_report1 = OrderFinanceReport.objects.create(
            order=order1,
            earned_amount=1000.0
        )
        
        finance_report2 = OrderFinanceReport.objects.create(
            order=order2,
            earned_amount=2000.0
        )
        
        finance_report3 = OrderFinanceReport.objects.create(
            order=order3,
            earned_amount=3000.0
        )
        
        # Filter today's orders
        today_reports = OrderFinanceReport.objects.filter(
            order__creation_date__date=today.date()
        )
        
        # Bir bugünkü report olmalı
        self.assertTrue(today_reports.exists())
        self.assertEqual(today_reports.count(), 1)
        
        # Tüm report'ları al
        all_reports = OrderFinanceReport.objects.all()
        self.assertEqual(all_reports.count(), 3)
    
    def test_order_finance_report_aggregation(self):
        """OrderFinanceReport total calculation test"""
        # Create multiple orders and finance reports
        orders_list = []
        for i in range(5):
            order = orders.objects.create(
                order_day=timezone.now(),
                order_name=f'Order {i+1}',
                order_description=f'Order {i+1} description',
                organisation=self.organisor_profile,
                lead=self.lead
            )
            orders_list.append(order)
            
            OrderFinanceReport.objects.create(
                order=order,
                earned_amount=1000.0 * (i + 1)  # 1000, 2000, 3000, 4000, 5000
            )
        
        # Calculate total earned
        from django.db.models import Sum
        total_earned = OrderFinanceReport.objects.aggregate(
            total=Sum('earned_amount')
        )['total']
        
        expected_total = 1000 + 2000 + 3000 + 4000 + 5000  # 15000
        self.assertEqual(total_earned, expected_total)
    
    def test_order_finance_report_organisation_filtering(self):
        """OrderFinanceReport organizasyon filtreleme testi"""
        # Create different organisations
        org2_user = User.objects.create_user(
            username='org2_finance_test',
            email='org2_finance_test@example.com',
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
        
        # Filter only org1's finance reports
        org1_reports = OrderFinanceReport.objects.filter(
            order__organisation=self.organisor_profile
        )
        
        self.assertEqual(org1_reports.count(), 1)
        self.assertEqual(org1_reports.first(), finance_report1)


if __name__ == "__main__":
    print("Finance Models Testleri Başlatılıyor...")
    print("=" * 60)
    
    # Test çalıştırma
    import unittest
    unittest.main()
