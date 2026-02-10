"""
ProductsAndStock Integration Tests
This file tests all components of the ProductsAndStock module working together.
"""

from django.test import TestCase, TransactionTestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import transaction
from decimal import Decimal

from ProductsAndStock.models import (
    ProductsAndStock, Category, SubCategory, StockMovement, 
    PriceHistory, SalesStatistics, StockAlert, StockRecommendation
)
from ProductsAndStock.forms import ProductAndStockModelForm, AdminProductAndStockModelForm
from ProductsAndStock.bulk_price_form import BulkPriceUpdateForm
from leads.models import UserProfile
# from agents.models import Agent  # Agent model not available

User = get_user_model()

SIMPLE_STATIC = {'STATICFILES_STORAGE': 'django.contrib.staticfiles.storage.StaticFilesStorage'}


@override_settings(**SIMPLE_STATIC)
class TestProductsAndStockWorkflow(TestCase):
    """ProductsAndStock full workflow tests"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create users
        self.admin_user = User.objects.create_user(
            username="admin_integration_main",
            email="admin_integration_main@example.com",
            password="adminpass123",
            is_superuser=True
        )
        
        self.organisor_user = User.objects.create_user(
            username="organisor_integration_main",
            email="organisor_integration_main@example.com",
            password="organisorpass123",
            is_organisor=True
        )
        self.organisor_profile, created = UserProfile.objects.get_or_create(
            user=self.organisor_user
        )
        
        self.agent_user = User.objects.create_user(
            username="agent_integration_main",
            email="agent_integration_main@example.com",
            password="agentpass123",
            is_agent=True
        )
        self.agent_profile, created = UserProfile.objects.get_or_create(
            user=self.agent_user
        )
        # Agent model not available, use user only
        # self.agent = Agent.objects.create(
        #     user=self.agent_user,
        #     organisation=self.organisor_profile
        # )
        
        # Create category and subcategory
        self.category = Category.objects.create(name="Electronics")
        self.subcategory = SubCategory.objects.create(
            name="Smartphones",
            category=self.category
        )
    
    def test_complete_product_lifecycle(self):
        """Full product lifecycle test"""
        # 1. Create product
        product_data = {
            'product_name': 'iPhone 15 Pro',
            'product_description': 'Latest iPhone with advanced features',
            'product_price': 1199.99,
            'cost_price': 1000.00,
            'product_quantity': 100,
            'minimum_stock_level': 20,
            'category': self.category.id,
            'subcategory': self.subcategory.id,
            'discount_percentage': 0,
            'discount_amount': 0,
        }
        
        self.client.force_login(self.organisor_user)
        
        # Create product
        response = self.client.post(reverse('ProductsAndStock:ProductAndStock-create'), product_data)
        self.assertEqual(response.status_code, 302)
        
        # Check if product was created
        product = ProductsAndStock.objects.get(product_name='iPhone 15 Pro')
        self.assertEqual(product.product_price, 1199.99)
        self.assertEqual(product.product_quantity, 100)
        self.assertEqual(product.organisation, self.organisor_profile)
        
        # 2. Check if stock movement was created
        stock_movements = StockMovement.objects.filter(product=product)
        self.assertEqual(stock_movements.count(), 1)
        self.assertEqual(stock_movements.first().movement_type, 'IN')
        self.assertEqual(stock_movements.first().quantity_change, 100)
        
        # 3. View product detail page
        response = self.client.get(
            reverse('ProductsAndStock:ProductAndStock-detail', kwargs={'pk': product.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'iPhone 15 Pro')
        
        # 4. Update product
        update_data = {
            'product_name': 'iPhone 15 Pro Max',
            'product_description': 'Updated iPhone with advanced features',
            'product_price': 1299.99,  # Price increase
            'cost_price': 1100.00,
            'product_quantity': 80,  # Stock decrease
            'minimum_stock_level': 25,
            'category': self.category.id,
            'subcategory': self.subcategory.id,
            'discount_percentage': 0,
            'discount_amount': 0,
        }
        
        response = self.client.post(
            reverse('ProductsAndStock:ProductAndStock-update', kwargs={'pk': product.pk}),
            update_data
        )
        self.assertEqual(response.status_code, 302)
        
        # Check if product was updated
        updated_product = ProductsAndStock.objects.get(pk=product.pk)
        self.assertEqual(updated_product.product_name, 'iPhone 15 Pro Max')
        self.assertEqual(updated_product.product_price, 1299.99)
        self.assertEqual(updated_product.product_quantity, 80)
        
        # 5. Check if price history was created
        price_history = PriceHistory.objects.filter(product=updated_product)
        self.assertTrue(price_history.exists())
        latest_price_change = price_history.first()
        self.assertEqual(latest_price_change.old_price, 1199.99)
        self.assertEqual(latest_price_change.new_price, 1299.99)
        self.assertEqual(latest_price_change.price_change, 100.0)
        
        # 6. Check if stock movement was created
        stock_movements = StockMovement.objects.filter(product=updated_product)
        self.assertEqual(stock_movements.count(), 2)  # Initial create + update
        latest_movement = stock_movements.first()
        self.assertEqual(latest_movement.movement_type, 'OUT')
        self.assertEqual(latest_movement.quantity_change, -20)
        
        # 7. Create low stock alert
        updated_product.product_quantity = 5  # Below minimum stock level
        updated_product.save()
        
        # Check if stock alert was created
        stock_alerts = StockAlert.objects.filter(product=updated_product)
        self.assertTrue(stock_alerts.exists())
        self.assertEqual(stock_alerts.first().alert_type, 'LOW_STOCK')
        
        # 8. Check if stock recommendation was created
        stock_recommendations = StockRecommendation.objects.filter(product=updated_product)
        self.assertTrue(stock_recommendations.exists())
        self.assertEqual(stock_recommendations.first().recommendation_type, 'RESTOCK')
        
        # 9. View product list
        response = self.client.get(reverse('ProductsAndStock:ProductAndStock-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'iPhone 15 Pro Max')
        
        # 10. View dashboard
        response = self.client.get(reverse('ProductsAndStock:sales-dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard')
        
        # 11. Delete product
        response = self.client.post(
            reverse('ProductsAndStock:ProductAndStock-delete', kwargs={'pk': updated_product.pk})
        )
        self.assertEqual(response.status_code, 302)
        
        # Check if product was deleted
        self.assertFalse(ProductsAndStock.objects.filter(pk=updated_product.pk).exists())
    
    def test_bulk_price_update_workflow(self):
        """Bulk price update workflow test"""
        # Create test products
        products = []
        for i in range(3):
            product = ProductsAndStock.objects.create(
                product_name=f'Product {i+1}',
                product_description=f'Test product {i+1}',
                product_price=100.0 + (i * 50),
                cost_price=80.0 + (i * 40),
                product_quantity=50 + (i * 10),
                minimum_stock_level=10,
                category=self.category,
                subcategory=self.subcategory,
                organisation=self.organisor_profile
            )
            products.append(product)
        
        self.client.force_login(self.organisor_user)
        
        # Bulk price update form
        bulk_data = {
            'update_type': 'PERCENTAGE_INCREASE',
            'category_filter': 'ALL',
            'percentage_increase': 15.0,
            'reason': 'Market price increase'
        }
        
        response = self.client.post(reverse('ProductsAndStock:bulk-price-update'), bulk_data)
        self.assertEqual(response.status_code, 302)
        
        # Check if all product prices were updated
        for i, product in enumerate(products):
            updated_product = ProductsAndStock.objects.get(pk=product.pk)
            expected_price = (100.0 + (i * 50)) * 1.15
            self.assertAlmostEqual(updated_product.product_price, expected_price, places=2)
            
            # Check if price history was created
            price_history = PriceHistory.objects.filter(product=updated_product)
            self.assertTrue(price_history.exists())
            self.assertEqual(price_history.first().change_type, 'INCREASE')
    
    def test_stock_alert_system(self):
        """Stock alert system test"""
        # Create product with low stock level
        product = ProductsAndStock.objects.create(
            product_name='Low Stock Product',
            product_description='Product with low stock',
            product_price=99.99,
            cost_price=80.00,
            product_quantity=5,  # Low stock
            minimum_stock_level=10,
            category=self.category,
            subcategory=self.subcategory,
            organisation=self.organisor_profile
        )
        
        # Check if stock alert was created
        stock_alerts = StockAlert.objects.filter(product=product)
        self.assertTrue(stock_alerts.exists())
        self.assertEqual(stock_alerts.first().alert_type, 'LOW_STOCK')
        self.assertEqual(stock_alerts.first().severity, 'CRITICAL')
        
        # Check if stock recommendation was created
        stock_recommendations = StockRecommendation.objects.filter(product=product)
        self.assertTrue(stock_recommendations.exists())
        self.assertEqual(stock_recommendations.first().recommendation_type, 'RESTOCK')
        
        # Warning when stock is depleted
        product.product_quantity = 0
        product.save()
        
        # Check if out of stock alert was created
        out_of_stock_alerts = StockAlert.objects.filter(
            product=product,
            alert_type='OUT_OF_STOCK'
        )
        self.assertTrue(out_of_stock_alerts.exists())
        self.assertEqual(out_of_stock_alerts.first().severity, 'CRITICAL')
    
    def test_discount_system(self):
        """Discount system test"""
        # Create product with discount
        product = ProductsAndStock.objects.create(
            product_name='Discounted Product',
            product_description='Product with discount',
            product_price=100.0,
            cost_price=80.0,
            product_quantity=50,
            minimum_stock_level=10,
            category=self.category,
            subcategory=self.subcategory,
            organisation=self.organisor_profile,
            discount_percentage=20.0,
            discount_amount=10.0
        )
        
        # Discounted price calculation test
        expected_discounted_price = (100.0 * 0.8) - 10.0  # 20% discount + 10 fixed discount
        self.assertEqual(product.discounted_price, expected_discounted_price)
        
        # Check if discount is active
        self.assertTrue(product.is_discount_active)
        
        # Scheduled discount test
        now = timezone.now()
        product.discount_start_date = now + timezone.timedelta(days=1)
        product.discount_end_date = now + timezone.timedelta(days=2)
        product.save()
        
        # Future discount is not active
        self.assertFalse(product.is_discount_active)
        
        # Active scheduled discount
        product.discount_start_date = now - timezone.timedelta(hours=1)
        product.discount_end_date = now + timezone.timedelta(hours=1)
        product.save()
        
        # Active scheduled discount
        self.assertTrue(product.is_discount_active)
    
    def test_profit_calculation_system(self):
        """Profit calculation system test"""
        product = ProductsAndStock.objects.create(
            product_name='Profit Test Product',
            product_description='Product for profit testing',
            product_price=150.0,
            cost_price=100.0,
            product_quantity=20,
            minimum_stock_level=5,
            category=self.category,
            subcategory=self.subcategory,
            organisation=self.organisor_profile
        )
        
        # Profit margin amount
        expected_profit_margin = 150.0 - 100.0
        self.assertEqual(product.profit_margin_amount, expected_profit_margin)
        
        # Profit margin percentage
        expected_profit_percentage = (50.0 / 100.0) * 100
        self.assertEqual(product.profit_margin_percentage, expected_profit_percentage)
        
        # Total profit
        expected_total_profit = 50.0 * 20
        self.assertEqual(product.total_profit, expected_total_profit)
        
        # Total value
        expected_total_value = 150.0 * 20
        self.assertEqual(product.total_value, expected_total_value)
    
    def test_category_subcategory_workflow(self):
        """Category-subcategory workflow test"""
        # Create new category
        new_category = Category.objects.create(name="Books")
        new_subcategory = SubCategory.objects.create(
            name="Fiction",
            category=new_category
        )
        
        # Create product
        product = ProductsAndStock.objects.create(
            product_name='Book Product',
            product_description='A fiction book',
            product_price=25.0,
            cost_price=15.0,
            product_quantity=100,
            minimum_stock_level=20,
            category=new_category,
            subcategory=new_subcategory,
            organisation=self.organisor_profile
        )
        
        # Check if category relations are correct
        self.assertEqual(product.category, new_category)
        self.assertEqual(product.subcategory, new_subcategory)
        self.assertIn(product, new_category.productsandstock_set.all())
        self.assertIn(product, new_subcategory.productsandstock_set.all())
        
        # Check if subcategory belongs to category
        self.assertEqual(new_subcategory.category, new_category)
        self.assertIn(new_subcategory, new_category.subcategories.all())
    
    def test_user_permissions_workflow(self):
        """User permissions workflow test"""
        # Test with agent user
        self.client.force_login(self.agent_user)

        # Can agent see product list
        response = self.client.get(reverse('ProductsAndStock:ProductAndStock-list'))
        self.assertEqual(response.status_code, 200)
        
        # Can agent create product (no)
        response = self.client.get(reverse('ProductsAndStock:ProductAndStock-create'))
        self.assertEqual(response.status_code, 200)  # Agent can create products
        
        # Test with organisor user
        self.client.force_login(self.organisor_user)
        
        # Can organisor create product
        response = self.client.get(reverse('ProductsAndStock:ProductAndStock-create'))
        self.assertEqual(response.status_code, 200)
        
        # Test with admin user
        self.client.force_login(self.admin_user)
        
        # Can admin perform all operations
        response = self.client.get(reverse('ProductsAndStock:ProductAndStock-list'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('ProductsAndStock:ProductAndStock-create'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('ProductsAndStock:bulk-price-update'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('ProductsAndStock:sales-dashboard'))
        self.assertEqual(response.status_code, 200)
    
    def test_ajax_subcategory_loading(self):
        """AJAX subcategory loading test"""
        # Load subcategories with category selection
        response = self.client.get(
            reverse('ProductsAndStock:get-subcategories'),
            {'category_id': self.category.id}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('subcategories', data)
        self.assertEqual(len(data['subcategories']), 1)
        self.assertEqual(data['subcategories'][0]['name'], 'Smartphones')
    
    def test_form_validation_integration(self):
        """Form validation integration test"""
        # Form test with invalid data
        invalid_data = {
            'product_name': '',  # Empty name
            'product_description': 'Test Description',
            'product_price': -10,  # Negative price
            'cost_price': 80.00,
            'product_quantity': 10,
            'minimum_stock_level': 2,
            'category': self.category.id,
            'subcategory': self.subcategory.id,
        }
        
        form = ProductAndStockModelForm(data=invalid_data)
        form.user_organisation = self.organisor_profile
        
        self.assertFalse(form.is_valid())
        self.assertIn('product_name', form.errors)
    
    def test_database_transactions(self):
        """Database operations test"""
        # Create product with transaction
        with transaction.atomic():
            product = ProductsAndStock.objects.create(
                product_name='Transaction Test Product',
                product_description='Product for transaction testing',
                product_price=99.99,
                cost_price=80.00,
                product_quantity=10,
                minimum_stock_level=2,
                category=self.category,
                subcategory=self.subcategory,
                organisation=self.organisor_profile
            )
            
            # Check if stock movement was created
            stock_movements = StockMovement.objects.filter(product=product)
            self.assertEqual(stock_movements.count(), 1)
    
    def test_performance_with_multiple_products(self):
        """Multiple product performance test"""
        # Create many products
        products = []
        for i in range(50):
            product = ProductsAndStock.objects.create(
                product_name=f'Performance Test Product {i}',
                product_description=f'Product {i} for performance testing',
                product_price=100.0 + i,
                cost_price=80.0 + i,
                product_quantity=50 + i,
                minimum_stock_level=10,
                category=self.category,
                subcategory=self.subcategory,
                organisation=self.organisor_profile
            )
            products.append(product)
        
        # List page performance
        self.client.force_login(self.organisor_user)
        
        import time
        start_time = time.time()
        response = self.client.get(reverse('ProductsAndStock:ProductAndStock-list'))
        end_time = time.time()
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(end_time - start_time, 2.0)  # Should be less than 2 seconds
        
        # Dashboard performance
        start_time = time.time()
        response = self.client.get(reverse('ProductsAndStock:sales-dashboard'))
        end_time = time.time()
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(end_time - start_time, 3.0)  # Should be less than 3 seconds


class TestProductsAndStockSignals(TransactionTestCase):
    """ProductsAndStock signals tests"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            is_organisor=True
        )
        self.user_profile, created = UserProfile.objects.get_or_create(
            user=self.user
        )
        
        self.category = Category.objects.create(name="Electronics")
        self.subcategory = SubCategory.objects.create(
            name="Smartphones",
            category=self.category
        )
    
    def test_product_creation_signals(self):
        """Product creation signals test"""
        # Create product
        product = ProductsAndStock.objects.create(
            product_name='Signal Test Product',
            product_description='Product for signal testing',
            product_price=99.99,
            cost_price=80.00,
            product_quantity=50,
            minimum_stock_level=10,
            category=self.category,
            subcategory=self.subcategory,
            organisation=self.user_profile
        )
        
        # Check if stock movement was created
        stock_movements = StockMovement.objects.filter(product=product)
        self.assertEqual(stock_movements.count(), 1)
        self.assertEqual(stock_movements.first().movement_type, 'IN')
        self.assertEqual(stock_movements.first().quantity_change, 50)
    
    def test_product_update_signals(self):
        """Product update signals test"""
        # Create product
        product = ProductsAndStock.objects.create(
            product_name='Signal Update Test Product',
            product_description='Product for signal update testing',
            product_price=99.99,
            cost_price=80.00,
            product_quantity=50,
            minimum_stock_level=10,
            category=self.category,
            subcategory=self.subcategory,
            organisation=self.user_profile
        )
        
        # Update price
        product.product_price = 149.99
        product.save()
        
        # Check if price history was created
        price_history = PriceHistory.objects.filter(product=product)
        self.assertEqual(price_history.count(), 1)
        self.assertEqual(price_history.first().old_price, 99.99)
        self.assertEqual(price_history.first().new_price, 149.99)
        self.assertAlmostEqual(price_history.first().price_change, 50.0, places=2)
        
        # Update stock
        product.product_quantity = 30
        product.save()
        
        # Check if stock movement was created
        stock_movements = StockMovement.objects.filter(product=product)
        self.assertEqual(stock_movements.count(), 2)  # Initial create + update
        latest_movement = stock_movements.first()
        self.assertEqual(latest_movement.movement_type, 'OUT')
        self.assertEqual(latest_movement.quantity_change, -20)
    
    def test_low_stock_alert_signals(self):
        """Low stock alert signals test"""
        # Create product with low stock level
        product = ProductsAndStock.objects.create(
            product_name='Low Stock Signal Test Product',
            product_description='Product for low stock signal testing',
            product_price=99.99,
            cost_price=80.00,
            product_quantity=5,  # Low stock
            minimum_stock_level=10,
            category=self.category,
            subcategory=self.subcategory,
            organisation=self.user_profile
        )
        
        # Check if stock alert was created
        stock_alerts = StockAlert.objects.filter(product=product)
        self.assertTrue(stock_alerts.exists())
        self.assertEqual(stock_alerts.first().alert_type, 'LOW_STOCK')
        
        # Check if stock recommendation was created
        stock_recommendations = StockRecommendation.objects.filter(product=product)
        self.assertTrue(stock_recommendations.exists())
        self.assertEqual(stock_recommendations.first().recommendation_type, 'RESTOCK')
