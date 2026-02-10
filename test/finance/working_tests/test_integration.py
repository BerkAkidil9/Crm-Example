"""
Finance Integration Test File
This file tests the integration of the Finance module with other modules.
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

# Load Django settings
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
    """Finance-Orders integration tests"""
    
    def setUp(self):
        """Set up test data"""
        # Create organisor user
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
        
        # Create category and products
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
        """Order creation with finance report integration"""
        # Create Order
        order = orders.objects.create(
            order_day=timezone.now(),
            order_name='Integration Test Order',
            order_description='Order for integration testing',
            organisation=self.organisor_profile,
            lead=self.lead
        )
        
        # Create OrderProducts
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
        
        # Create finance report
        finance_report = OrderFinanceReport.objects.create(
            order=order,
            earned_amount=total_earned
        )
        
        # Integration verification
        self.assertEqual(finance_report.order, order)
        self.assertEqual(finance_report.earned_amount, total_earned)
        self.assertEqual(order.orderfinancereport, finance_report)
        
        # Access products from Order
        self.assertEqual(order.products.count(), 2)
        self.assertIn(self.product1, order.products.all())
        self.assertIn(self.product2, order.products.all())
    
    def test_order_cancellation_finance_report_impact(self):
        """Order cancellation finance report impact"""
        # Create Order
        order = orders.objects.create(
            order_day=timezone.now(),
            order_name='Cancellation Test Order',
            order_description='Order for cancellation testing',
            organisation=self.organisor_profile,
            lead=self.lead
        )
        
        # Create OrderProduct
        order_product = OrderProduct.objects.create(
            order=order,
            product=self.product1,
            product_quantity=5
        )
        
        # Create finance report
        finance_report = OrderFinanceReport.objects.create(
            order=order,
            earned_amount=order_product.total_price
        )
        
        # Cancel Order
        order.is_cancelled = True
        order.save()
        
        # Finance report should still exist (reports can be kept for cancelled orders)
        self.assertTrue(OrderFinanceReport.objects.filter(id=finance_report.id).exists())
        self.assertEqual(order.orderfinancereport, finance_report)
    
    def test_order_deletion_finance_report_cascade(self):
        """Order deletion finance report cascade test"""
        # Create Order
        order = orders.objects.create(
            order_day=timezone.now(),
            order_name='Deletion Test Order',
            order_description='Order for deletion testing',
            organisation=self.organisor_profile,
            lead=self.lead
        )
        
        # Create finance report
        finance_report = OrderFinanceReport.objects.create(
            order=order,
            earned_amount=1000.0
        )
        
        finance_report_id = finance_report.id
        
        # Delete Order
        order.delete()
        
        # Finance report should also be deleted (CASCADE)
        self.assertFalse(OrderFinanceReport.objects.filter(id=finance_report_id).exists())
    
    def test_multiple_orders_finance_reports_aggregation(self):
        """Multiple orders finance report aggregation"""
        orders_list = []
        total_expected_earned = 0
        
        # Create multiple orders
        for i in range(3):
            order = orders.objects.create(
                order_day=timezone.now(),
                order_name=f'Order {i+1}',
                order_description=f'Order {i+1} description',
                organisation=self.organisor_profile,
                lead=self.lead
            )
            orders_list.append(order)
            
            # Different product and quantity for each order
            product = self.product1 if i % 2 == 0 else self.product2
            quantity = (i + 1) * 2
            
            order_product = OrderProduct.objects.create(
                order=order,
                product=product,
                product_quantity=quantity
            )
            
            # Create finance report
            earned_amount = order_product.total_price
            total_expected_earned += earned_amount
            
            OrderFinanceReport.objects.create(
                order=order,
                earned_amount=earned_amount
            )
        
        # Calculate total earned
        from django.db.models import Sum
        total_earned = OrderFinanceReport.objects.aggregate(
            total=Sum('earned_amount')
        )['total']
        
        self.assertEqual(total_earned, total_expected_earned)
        self.assertEqual(OrderFinanceReport.objects.count(), 3)
    
    def test_finance_report_date_filtering_with_orders(self):
        """Finance report date filtering integration with orders"""
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
                creation_date=order_date  # set creation_date manually
            )
            
            OrderFinanceReport.objects.create(
                order=order,
                earned_amount=1000.0
            )
        
        # Filter today's orders
        today_reports = OrderFinanceReport.objects.filter(
            order__creation_date__date=today.date()
        )
        
        self.assertEqual(today_reports.count(), 1)  # Only today's order
        self.assertIn('Today Order', [report.order.order_name for report in today_reports])
    
    def test_finance_report_organisation_filtering(self):
        """Finance report organisation filtering"""
        # Create different organisation
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
        
        # Create order and finance report for each organisation
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
        
        # Filter only org2's finance reports
        org2_reports = OrderFinanceReport.objects.filter(
            order__organisation=org2_profile
        )
        
        self.assertEqual(org2_reports.count(), 1)
        self.assertEqual(org2_reports.first(), finance_report2)


class TestFinanceProductsIntegration(TestCase):
    """Finance-Products integration tests"""
    
    def setUp(self):
        """Set up test data"""
        # Create organisor user
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
        
        # Create category and products
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
        """Finance report product profit calculation integration"""
        # Create Order
        order = orders.objects.create(
            order_day=timezone.now(),
            order_name='Profit Calculation Order',
            order_description='Order for profit calculation',
            organisation=self.organisor_profile,
            lead=self.lead
        )
        
        # Create OrderProduct
        order_product = OrderProduct.objects.create(
            order=order,
            product=self.product1,
            product_quantity=2
        )
        
        # Create finance report
        finance_report = OrderFinanceReport.objects.create(
            order=order,
            earned_amount=order_product.total_price
        )
        
        # Profit calculation
        total_revenue = order_product.total_price
        total_cost = order_product.product_quantity * order_product.product.cost_price
        profit = total_revenue - total_cost
        
        # Profit calculation verification
        expected_profit = 2 * (self.product1.product_price - self.product1.cost_price)
        self.assertEqual(profit, expected_profit)
        self.assertEqual(finance_report.earned_amount, total_revenue)
    
    def test_finance_report_multiple_products_profit(self):
        """Finance report multiple products profit calculation"""
        # Create Order
        order = orders.objects.create(
            order_day=timezone.now(),
            order_name='Multiple Products Order',
            order_description='Order with multiple products',
            organisation=self.organisor_profile,
            lead=self.lead
        )
        
        # Create multiple OrderProducts
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
        
        # Calculate total revenue and cost
        total_revenue = order_product1.total_price + order_product2.total_price
        total_cost = (order_product1.product_quantity * order_product1.product.cost_price + 
                     order_product2.product_quantity * order_product2.product.cost_price)
        total_profit = total_revenue - total_cost
        
        # Create finance report
        finance_report = OrderFinanceReport.objects.create(
            order=order,
            earned_amount=total_revenue
        )
        
        # Verify calculations
        self.assertEqual(finance_report.earned_amount, total_revenue)
        self.assertGreater(total_profit, 0)  # Profit should be positive
        
        # Expected profit calculation (use almost equal for float precision)
        expected_profit = (2 * (self.product1.product_price - self.product1.cost_price) + 
                          3 * (self.product2.product_price - self.product2.cost_price))
        self.assertAlmostEqual(total_profit, expected_profit, places=2)
    
    def test_finance_report_stock_movement_integration(self):
        """Finance report stock movement integration"""
        # Create Order
        order = orders.objects.create(
            order_day=timezone.now(),
            order_name='Stock Movement Order',
            order_description='Order for stock movement testing',
            organisation=self.organisor_profile,
            lead=self.lead
        )
        
        # Create OrderProduct (stock will be reduced)
        order_product = OrderProduct.objects.create(
            order=order,
            product=self.product1,
            product_quantity=5
        )
        
        # Create finance report
        finance_report = OrderFinanceReport.objects.create(
            order=order,
            earned_amount=order_product.total_price
        )
        
        # Stock movement should have been created
        stock_movements = StockMovement.objects.filter(
            product=self.product1,
            movement_type='OUT'
        )
        
        self.assertTrue(stock_movements.exists())
        
        # Stock quantity should have been reduced
        self.product1.refresh_from_db()
        expected_stock = 50 - 5  # Initial stock - quantity
        self.assertEqual(self.product1.product_quantity, expected_stock)
        
        # Finance report and stock movement relationship
        self.assertEqual(finance_report.order, order)
        self.assertEqual(order.products.first(), self.product1)


class TestFinanceViewsIntegration(TestCase):
    """Finance Views integration tests"""
    
    def setUp(self):
        """Set up test data"""
        # Create organisor user
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
        
        # Date variables
        from datetime import datetime
        now = timezone.now()
        self.today = timezone.make_aware(datetime.combine(
            now.date(), datetime.min.time()
        ))
    
    def test_financial_report_view_full_workflow(self):
        """FinancialReportView full workflow test"""
        from django.test import Client
        
        client = Client()
        client.login(username='finance_views_integration', password='testpass123')
        
        # Create Order and finance report
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
        """FinancialReportView form integration"""
        from django.test import Client
        
        client = Client()
        client.login(username='finance_views_integration', password='testpass123')
        
        # GET request - form should be rendered
        response = client.get(reverse('finance:financial_report'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        
        # Form should be DateRangeForm
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
        # Returns GET response because form is invalid


class TestFinanceDataConsistency(TransactionTestCase):
    """Finance data consistency tests"""
    
    def setUp(self):
        """Set up test data"""
        # Create organisor user
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
    
    def test_finance_report_data_consistency(self):
        """Finance report data consistency test"""
        # Create Order
        order = orders.objects.create(
            order_day=timezone.now(),
            order_name='Consistency Test Order',
            order_description='Order for consistency testing',
            organisation=self.organisor_profile,
            lead=self.lead
        )
        
        # Create OrderProduct
        order_product = OrderProduct.objects.create(
            order=order,
            product=self.product,
            product_quantity=3
        )
        
        # Create finance report
        finance_report = OrderFinanceReport.objects.create(
            order=order,
            earned_amount=order_product.total_price
        )
        
        # Data consistency check
        self.assertEqual(finance_report.order, order)
        self.assertEqual(finance_report.earned_amount, order_product.total_price)
        self.assertEqual(order.orderfinancereport, finance_report)
        
        # Access products from Order
        self.assertEqual(order.products.count(), 1)
        self.assertEqual(order.products.first(), self.product)
        
        # Access order from OrderProduct
        self.assertEqual(order_product.order, order)
        self.assertEqual(order_product.product, self.product)
    
    def test_finance_report_unique_constraint(self):
        """Finance report unique constraint test"""
        # Create Order
        order = orders.objects.create(
            order_day=timezone.now(),
            order_name='Unique Constraint Order',
            order_description='Order for unique constraint testing',
            organisation=self.organisor_profile,
            lead=self.lead
        )
        
        # Create first finance report
        finance_report1 = OrderFinanceReport.objects.create(
            order=order,
            earned_amount=1000.0
        )
        
        # Try to create second finance report with same order
        with self.assertRaises(IntegrityError):
            OrderFinanceReport.objects.create(
                order=order,
                earned_amount=2000.0
            )
        
        # No rollback because we use TransactionTestCase
        # Only one finance report should exist
        self.assertEqual(OrderFinanceReport.objects.filter(order=order).count(), 1)
        self.assertEqual(OrderFinanceReport.objects.get(order=order), finance_report1)


if __name__ == "__main__":
    print("Starting Finance Integration Tests...")
    print("=" * 60)
    
    # Run tests
    import unittest
    unittest.main()
