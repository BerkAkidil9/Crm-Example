"""
Basit test dosyası - ProductsAndStock modülü için temel testler
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from leads.models import UserProfile
from ProductsAndStock.models import Category, SubCategory, ProductsAndStock

User = get_user_model()

class SimpleProductsAndStockTest(TestCase):
    """Basit ProductsAndStock testleri"""
    
    def setUp(self):
        """Test verilerini hazırla"""
        # Kullanıcı oluştur
        self.user = User.objects.create_user(
            username="testuser_simple",
            email="test_simple@example.com",
            password="testpass123"
        )
        
        # UserProfile oluştur (get_or_create kullan)
        self.user_profile, created = UserProfile.objects.get_or_create(user=self.user)
        
        # Kategori oluştur
        self.category = Category.objects.create(
            name="Test Category"
        )
        
        # Alt kategori oluştur
        self.subcategory = SubCategory.objects.create(
            name="Test SubCategory",
            category=self.category
        )
    
    def test_category_creation(self):
        """Kategori oluşturma testi"""
        self.assertEqual(self.category.name, "Test Category")
        # Category modelinde organisation alanı yok
    
    def test_subcategory_creation(self):
        """Alt kategori oluşturma testi"""
        self.assertEqual(self.subcategory.name, "Test SubCategory")
        self.assertEqual(self.subcategory.category, self.category)
    
    def test_product_creation(self):
        """Ürün oluşturma testi"""
        product = ProductsAndStock.objects.create(
            product_name="Test Product",
            product_description="Test Description",
            product_price=100.0,
            cost_price=80.0,
            product_quantity=10,
            minimum_stock_level=5,
            category=self.category,
            subcategory=self.subcategory,
            organisation=self.user_profile
        )
        
        self.assertEqual(product.product_name, "Test Product")
        self.assertEqual(product.product_price, 100.0)
        self.assertEqual(product.product_quantity, 10)
        self.assertEqual(product.category, self.category)
        self.assertEqual(product.subcategory, self.subcategory)
        self.assertEqual(product.organisation, self.user_profile)
    
    def test_product_properties(self):
        """Ürün property'leri testi"""
        product = ProductsAndStock.objects.create(
            product_name="Test Product 2",
            product_description="Test Description 2",
            product_price=100.0,
            cost_price=80.0,
            product_quantity=10,
            minimum_stock_level=5,
            category=self.category,
            subcategory=self.subcategory,
            organisation=self.user_profile
        )
        
        # Total value testi
        expected_total_value = product.product_price * product.product_quantity
        self.assertEqual(product.total_value, expected_total_value)
        
        # Profit margin testi
        expected_profit_margin = product.product_price - product.cost_price
        self.assertEqual(product.profit_margin_amount, expected_profit_margin)
        
        # Stock status testi
        self.assertFalse(product.is_low_stock)  # 10 > 5 (minimum_stock_level)
    
    def test_product_str_representation(self):
        """Ürün __str__ metodu testi"""
        product = ProductsAndStock.objects.create(
            product_name="Test Product 3",
            product_description="Test Description 3",
            product_price=100.0,
            cost_price=80.0,
            product_quantity=10,
            minimum_stock_level=5,
            category=self.category,
            subcategory=self.subcategory,
            organisation=self.user_profile
        )
        
        expected_str = product.product_name  # ProductsAndStock __str__ sadece product_name döndürüyor
        self.assertEqual(str(product), expected_str)
