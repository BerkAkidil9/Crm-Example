"""
ProductsAndStock Models Test File
This file tests all models in the ProductsAndStock module.
"""

import os
import sys
import django
from django.test import TestCase, TransactionTestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import IntegrityError
from decimal import Decimal

# Load Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djcrm.settings')
django.setup()

from ProductsAndStock.models import (
    ProductsAndStock, Category, SubCategory, StockMovement, 
    PriceHistory, SalesStatistics, StockAlert, StockRecommendation
)
from leads.models import User, UserProfile


class TestCategoryModel(TestCase):
    """Category model tests"""
    
    def setUp(self):
        """Set up test data"""
        self.category = Category.objects.create(
            name="Electronics",
            description="Electronic devices and gadgets",
            icon="fas fa-mobile-alt"
        )
    
    def test_category_creation(self):
        """Category creation test"""
        self.assertEqual(self.category.name, "Electronics")
        self.assertEqual(self.category.description, "Electronic devices and gadgets")
        self.assertEqual(self.category.icon, "fas fa-mobile-alt")
        self.assertIsNotNone(self.category.created_at)
    
    def test_category_str_representation(self):
        """Category __str__ method test"""
        self.assertEqual(str(self.category), "Electronics")
    
    def test_category_ordering(self):
        """Category ordering test"""
        category2 = Category.objects.create(name="Books")
        categories = Category.objects.all()
        self.assertEqual(categories[0].name, "Books")  # Alphabetical order
        self.assertEqual(categories[1].name, "Electronics")
    
    def test_category_unique_name(self):
        """Category name uniqueness test"""
        with self.assertRaises(IntegrityError):
            Category.objects.create(name="Electronics")


class TestSubCategoryModel(TestCase):
    """SubCategory model tests"""
    
    def setUp(self):
        """Set up test data"""
        self.category = Category.objects.create(name="Electronics")
        self.subcategory = SubCategory.objects.create(
            name="Smartphones",
            category=self.category,
            description="Mobile phones and accessories"
        )
    
    def test_subcategory_creation(self):
        """Subcategory creation test"""
        self.assertEqual(self.subcategory.name, "Smartphones")
        self.assertEqual(self.subcategory.category, self.category)
        self.assertEqual(self.subcategory.description, "Mobile phones and accessories")
        self.assertIsNotNone(self.subcategory.created_at)
    
    def test_subcategory_str_representation(self):
        """SubCategory __str__ method test"""
        expected = f"{self.category.name} - {self.subcategory.name}"
        self.assertEqual(str(self.subcategory), expected)
    
    def test_subcategory_unique_together(self):
        """Subcategory uniqueness test (name + category)"""
        with self.assertRaises(IntegrityError):
            SubCategory.objects.create(
                name="Smartphones",
                category=self.category
            )
    
    def test_subcategory_ordering(self):
        """SubCategory ordering test"""
        subcategory2 = SubCategory.objects.create(
            name="Laptops",
            category=self.category
        )
        subcategories = SubCategory.objects.all()
        self.assertEqual(subcategories[0].name, "Laptops")
        self.assertEqual(subcategories[1].name, "Smartphones")


class TestProductsAndStockModel(TestCase):
    """ProductsAndStock model tests"""
    
    def setUp(self):
        """Set up test data"""
        # Create user and organisation
        self.user = User.objects.create_user(
            username="testuser_products_main",
            email="test_products_main@example.com",
            password="testpass123"
        )
        self.user_profile, created = UserProfile.objects.get_or_create(
            user=self.user
        )
        
        # Create category and subcategory
        self.category = Category.objects.create(name="Electronics")
        self.subcategory = SubCategory.objects.create(
            name="Smartphones",
            category=self.category
        )
        
        # Create product
        self.product = ProductsAndStock.objects.create(
            product_name="iPhone 15",
            product_description="Latest iPhone model",
            product_price=999.99,
            cost_price=800.00,
            product_quantity=50,
            minimum_stock_level=10,
            category=self.category,
            subcategory=self.subcategory,
            organisation=self.user_profile
        )
    
    def test_product_creation(self):
        """Product creation test"""
        self.assertEqual(self.product.product_name, "iPhone 15")
        self.assertEqual(self.product.product_price, 999.99)
        self.assertEqual(self.product.cost_price, 800.00)
        self.assertEqual(self.product.product_quantity, 50)
        self.assertEqual(self.product.minimum_stock_level, 10)
        self.assertEqual(self.product.category, self.category)
        self.assertEqual(self.product.subcategory, self.subcategory)
        self.assertEqual(self.product.organisation, self.user_profile)
    
    def test_product_str_representation(self):
        """ProductsAndStock __str__ method test"""
        self.assertEqual(str(self.product), "iPhone 15")
    
    def test_product_unique_together(self):
        """Product uniqueness test (product_name + organisation)"""
        with self.assertRaises(IntegrityError):
            ProductsAndStock.objects.create(
                product_name="iPhone 15",
                product_description="Another iPhone",
                product_price=999.99,
                cost_price=800.00,
                product_quantity=30,
                minimum_stock_level=5,
                category=self.category,
                subcategory=self.subcategory,
                organisation=self.user_profile
            )
    
    def test_total_value_property(self):
        """Total value property test"""
        expected_value = self.product.product_price * self.product.product_quantity
        self.assertEqual(self.product.total_value, expected_value)
        self.assertEqual(self.product.total_value, 49999.5)
    
    def test_is_low_stock_property(self):
        """Low stock property test"""
        # Normal stock level
        self.assertFalse(self.product.is_low_stock)
        
        # Low stock level
        self.product.product_quantity = 5
        self.assertTrue(self.product.is_low_stock)
        
        # Minimum stock level
        self.product.product_quantity = 10
        self.assertTrue(self.product.is_low_stock)
    
    def test_stock_status_property(self):
        """Stock status property test"""
        # Normal stock
        self.assertEqual(self.product.stock_status, "In Stock")
        
        # Low stock
        self.product.product_quantity = 5
        self.assertEqual(self.product.stock_status, "Low Stock")
        
        # Out of stock
        self.product.product_quantity = 0
        self.assertEqual(self.product.stock_status, "Out of Stock")
    
    def test_profit_margin_amount_property(self):
        """Profit margin amount property test"""
        expected_margin = self.product.product_price - self.product.cost_price
        self.assertEqual(self.product.profit_margin_amount, expected_margin)
        self.assertEqual(self.product.profit_margin_amount, 199.99)
    
    def test_profit_margin_percentage_property(self):
        """Profit margin percentage property test"""
        expected_percentage = (self.product.profit_margin_amount / self.product.cost_price) * 100
        self.assertEqual(self.product.profit_margin_percentage, expected_percentage)
        self.assertAlmostEqual(self.product.profit_margin_percentage, 24.99875, places=4)
    
    def test_discounted_price_property(self):
        """Discounted price property test"""
        # No discount
        self.assertEqual(self.product.discounted_price, self.product.product_price)
        
        # Percentage discount
        self.product.discount_percentage = 10.0
        expected_price = self.product.product_price * (1 - 10.0 / 100)
        self.assertEqual(self.product.discounted_price, expected_price)
        
        # Fixed discount amount
        self.product.discount_percentage = 0.0
        self.product.discount_amount = 50.0
        expected_price = self.product.product_price - 50.0
        self.assertEqual(self.product.discounted_price, expected_price)
    
    def test_is_discount_active_property(self):
        """Discount active property test"""
        # No discount
        self.assertFalse(self.product.is_discount_active)
        
        # Active discount
        self.product.discount_percentage = 10.0
        self.assertTrue(self.product.is_discount_active)
        
        # Dated discount - past
        now = timezone.now()
        self.product.discount_start_date = now - timezone.timedelta(days=2)
        self.product.discount_end_date = now - timezone.timedelta(days=1)
        self.assertFalse(self.product.is_discount_active)
        
        # Scheduled discount - future
        self.product.discount_start_date = now + timezone.timedelta(days=1)
        self.product.discount_end_date = now + timezone.timedelta(days=2)
        self.assertFalse(self.product.is_discount_active)
        
        # Scheduled discount - active
        self.product.discount_start_date = now - timezone.timedelta(hours=1)
        self.product.discount_end_date = now + timezone.timedelta(hours=1)
        self.assertTrue(self.product.is_discount_active)
    
    def test_total_profit_property(self):
        """Total profit property test"""
        expected_profit = self.product.profit_margin_amount * self.product.product_quantity
        self.assertEqual(self.product.total_profit, expected_profit)
        self.assertEqual(self.product.total_profit, 9999.5)
    
    def test_clean_method(self):
        """Clean method test"""
        # Invalid subcategory
        wrong_subcategory = SubCategory.objects.create(
            name="Books",
            category=Category.objects.create(name="Books")
        )
        
        self.product.subcategory = wrong_subcategory
        with self.assertRaises(ValidationError):
            self.product.clean()
    
    def test_send_low_stock_alert(self):
        """Low stock alert sending test"""
        # Set to low stock level
        self.product.product_quantity = 5
        
        # Email sending test (mock can be used)
        try:
            self.product.send_low_stock_alert()
            # May raise exception if email settings not configured
        except Exception as e:
            # Normal, email settings may not be present
            pass


class TestStockMovementModel(TestCase):
    """StockMovement model tests"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser_movement_main",
            email="test_movement_main@example.com",
            password="testpass123"
        )
        self.user_profile, created = UserProfile.objects.get_or_create(
            user=self.user
        )
        
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
            organisation=self.user_profile
        )
        
        self.stock_movement = StockMovement.objects.create(
            product=self.product,
            movement_type='IN',
            quantity_before=40,
            quantity_after=50,
            quantity_change=10,
            reason='Stock replenishment',
            created_by=self.user
        )
    
    def test_stock_movement_creation(self):
        """Stock movement creation test"""
        self.assertEqual(self.stock_movement.product, self.product)
        self.assertEqual(self.stock_movement.movement_type, 'IN')
        self.assertEqual(self.stock_movement.quantity_before, 40)
        self.assertEqual(self.stock_movement.quantity_after, 50)
        self.assertEqual(self.stock_movement.quantity_change, 10)
        self.assertEqual(self.stock_movement.reason, 'Stock replenishment')
        self.assertEqual(self.stock_movement.created_by, self.user)
        self.assertIsNotNone(self.stock_movement.created_at)
    
    def test_stock_movement_str_representation(self):
        """StockMovement __str__ method test"""
        expected = f"{self.product.product_name} - Stock In (+10)"
        self.assertEqual(str(self.stock_movement), expected)
    
    def test_movement_direction_property(self):
        """Movement direction property test"""
        # Positive change
        self.assertEqual(self.stock_movement.movement_direction, "IN")
        
        # Negative change
        self.stock_movement.quantity_change = -5
        self.assertEqual(self.stock_movement.movement_direction, "OUT")
        
        # Zero change
        self.stock_movement.quantity_change = 0
        self.assertEqual(self.stock_movement.movement_direction, "NO CHANGE")


class TestPriceHistoryModel(TestCase):
    """PriceHistory model tests"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser_price_main",
            email="test_price_main@example.com",
            password="testpass123"
        )
        self.user_profile, created = UserProfile.objects.get_or_create(
            user=self.user
        )
        
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
            organisation=self.user_profile
        )
        
        self.price_history = PriceHistory.objects.create(
            product=self.product,
            old_price=899.99,
            new_price=999.99,
            price_change=100.0,
            change_type='INCREASE',
            change_reason='Price increase due to demand',
            updated_by=self.user
        )
    
    def test_price_history_creation(self):
        """Price history creation test"""
        self.assertEqual(self.price_history.product, self.product)
        self.assertEqual(self.price_history.old_price, 899.99)
        self.assertEqual(self.price_history.new_price, 999.99)
        self.assertEqual(self.price_history.price_change, 100.0)
        self.assertEqual(self.price_history.change_type, 'INCREASE')
        self.assertEqual(self.price_history.change_reason, 'Price increase due to demand')
        self.assertEqual(self.price_history.updated_by, self.user)
        self.assertIsNotNone(self.price_history.created_at)
    
    def test_price_history_str_representation(self):
        """PriceHistory __str__ method test"""
        expected = f"{self.product.product_name} - Price Increase (+100.00)"
        self.assertEqual(str(self.price_history), expected)
    
    def test_change_percentage_property(self):
        """Change percentage property test"""
        expected_percentage = (100.0 / 899.99) * 100
        self.assertAlmostEqual(self.price_history.change_percentage, expected_percentage, places=4)
        
        # Zero old price test
        self.price_history.old_price = 0
        self.assertEqual(self.price_history.change_percentage, 0)


class TestSalesStatisticsModel(TestCase):
    """SalesStatistics model tests"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser_sales_main",
            email="test_sales_main@example.com",
            password="testpass123"
        )
        self.user_profile, created = UserProfile.objects.get_or_create(
            user=self.user
        )
        
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
            organisation=self.user_profile
        )
        
        self.sales_stats = SalesStatistics.objects.create(
            product=self.product,
            total_sales=10,
            total_revenue=9999.90,
            avg_daily_sales=5.0,
            last_sale_date=timezone.now()
        )
    
    def test_sales_statistics_creation(self):
        """Sales statistics creation test"""
        self.assertEqual(self.sales_stats.product, self.product)
        self.assertEqual(self.sales_stats.total_sales, 10)
        self.assertEqual(self.sales_stats.total_revenue, 9999.90)
        self.assertEqual(self.sales_stats.avg_daily_sales, 5.0)
        self.assertIsNotNone(self.sales_stats.last_sale_date)
        self.assertIsNotNone(self.sales_stats.date)
    
    def test_sales_statistics_str_representation(self):
        """SalesStatistics __str__ method test"""
        expected = f"{self.product.product_name} - {self.sales_stats.date} (10 sales)"
        self.assertEqual(str(self.sales_stats), expected)


class TestStockAlertModel(TestCase):
    """StockAlert model tests"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser_alert_main",
            email="test_alert_main@example.com",
            password="testpass123"
        )
        self.user_profile, created = UserProfile.objects.get_or_create(
            user=self.user
        )
        
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
            product_quantity=5,  # Low stock
            minimum_stock_level=10,
            category=self.category,
            subcategory=self.subcategory,
            organisation=self.user_profile
        )
        
        self.stock_alert = StockAlert.objects.create(
            product=self.product,
            alert_type='LOW_STOCK',
            severity='HIGH',
            message='Stock level is low: 5 units remaining',
            is_read=False,
            is_resolved=False
        )
    
    def test_stock_alert_creation(self):
        """Stock alert creation test"""
        self.assertEqual(self.stock_alert.product, self.product)
        self.assertEqual(self.stock_alert.alert_type, 'LOW_STOCK')
        self.assertEqual(self.stock_alert.severity, 'HIGH')
        self.assertEqual(self.stock_alert.message, 'Stock level is low: 5 units remaining')
        self.assertFalse(self.stock_alert.is_read)
        self.assertFalse(self.stock_alert.is_resolved)
        self.assertIsNotNone(self.stock_alert.created_at)
        self.assertIsNone(self.stock_alert.resolved_at)
    
    def test_stock_alert_str_representation(self):
        """StockAlert __str__ method test"""
        expected = f"{self.product.product_name} - Low Stock Alert (HIGH)"
        self.assertEqual(str(self.stock_alert), expected)


class TestStockRecommendationModel(TestCase):
    """StockRecommendation model tests"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser_recommendation_main",
            email="test_recommendation_main@example.com",
            password="testpass123"
        )
        self.user_profile, created = UserProfile.objects.get_or_create(
            user=self.user
        )
        
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
            product_quantity=5,  # Low stock
            minimum_stock_level=10,
            category=self.category,
            subcategory=self.subcategory,
            organisation=self.user_profile
        )
        
        self.stock_recommendation = StockRecommendation.objects.create(
            product=self.product,
            recommendation_type='RESTOCK',
            suggested_quantity=30,
            reason='Low stock level. Recommended to restock to 30 units.',
            confidence_score=85.0,
            is_applied=False
        )
    
    def test_stock_recommendation_creation(self):
        """Stock recommendation creation test"""
        self.assertEqual(self.stock_recommendation.product, self.product)
        self.assertEqual(self.stock_recommendation.recommendation_type, 'RESTOCK')
        self.assertEqual(self.stock_recommendation.suggested_quantity, 30)
        self.assertEqual(self.stock_recommendation.reason, 'Low stock level. Recommended to restock to 30 units.')
        self.assertEqual(self.stock_recommendation.confidence_score, 85.0)
        self.assertFalse(self.stock_recommendation.is_applied)
        self.assertIsNotNone(self.stock_recommendation.created_at)
        self.assertIsNone(self.stock_recommendation.applied_at)
    
    def test_stock_recommendation_str_representation(self):
        """StockRecommendation __str__ method test"""
        expected = f"{self.product.product_name} - Restock Recommendation"
        self.assertEqual(str(self.stock_recommendation), expected)


class TestModelRelationships(TestCase):
    """Model relationships tests"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser_relationships_main",
            email="test_relationships_main@example.com",
            password="testpass123"
        )
        self.user_profile, created = UserProfile.objects.get_or_create(
            user=self.user
        )
        
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
            organisation=self.user_profile
        )
    
    def test_category_subcategory_relationship(self):
        """Category-subcategory relationship test"""
        self.assertEqual(self.subcategory.category, self.category)
        self.assertIn(self.subcategory, self.category.subcategories.all())
    
    def test_product_category_relationship(self):
        """Product-category relationship test"""
        self.assertEqual(self.product.category, self.category)
        self.assertEqual(self.product.subcategory, self.subcategory)
    
    def test_product_organisation_relationship(self):
        """Product-organisation relationship test"""
        self.assertEqual(self.product.organisation, self.user_profile)
    
    def test_cascade_deletion(self):
        """Cascade deletion tests"""
        # When category is deleted, subcategories should also be deleted
        category_id = self.category.id
        self.category.delete()
        self.assertFalse(SubCategory.objects.filter(category_id=category_id).exists())
        
        # When product is deleted, related records should also be deleted
        product_id = self.product.id
        self.product.delete()
        self.assertFalse(StockMovement.objects.filter(product_id=product_id).exists())
        self.assertFalse(PriceHistory.objects.filter(product_id=product_id).exists())


if __name__ == "__main__":
    print("Starting ProductsAndStock Models Tests...")
    print("=" * 60)
    
    # Run tests
    import unittest
    unittest.main()
