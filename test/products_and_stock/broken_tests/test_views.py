"""
ProductsAndStock Viewları Test Dosyası
Bu dosya ProductsAndStock modülündeki tüm viewları test eder.
"""

import os
import sys
import django
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from decimal import Decimal

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djcrm.settings')
django.setup()

from ProductsAndStock.models import (
    ProductsAndStock, Category, SubCategory, StockMovement, 
    PriceHistory, SalesStatistics, StockAlert, StockRecommendation
)
from leads.models import UserProfile
# from agents.models import Agent  # Agent modeli yok

User = get_user_model()


class TestProductAndStockListView(TestCase):
    """ProductAndStockListView tests"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Kullanıcılar oluştur
        self.admin_user = User.objects.create_user(
            username="admin_views_main",
            email="admin_views_main@example.com",
            password="adminpass123",
            is_superuser=True
        )
        
        self.organisor_user = User.objects.create_user(
            username="organisor_views_main",
            email="organisor_views_main@example.com",
            password="organisorpass123",
            is_organisor=True
        )
        self.organisor_profile, created = UserProfile.objects.get_or_create(
            user=self.organisor_user
        )
        if created:
            self.organisor_profile.save()  # Ensure pk is assigned
        
        self.agent_user = User.objects.create_user(
            username="agent_views_main",
            email="agent_views_main@example.com",
            password="agentpass123",
            is_agent=True
        )
        self.agent_profile, created = UserProfile.objects.get_or_create(
            user=self.agent_user
        )
        if created:
            self.agent_profile.save()  # Ensure pk is assigned
        # Agent modeli yok, sadece user kullan
        # self.agent = Agent.objects.create(
        #     user=self.agent_user,
        #     organisation=self.organisor_profile
        # )
        
        # Kategori ve alt kategori oluştur
        self.category = Category.objects.create(name="Electronics")
        self.subcategory = SubCategory.objects.create(
            name="Smartphones",
            category=self.category
        )
        
        # Ürünler oluştur
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
            product_description="Android smartphone",
            product_price=799.99,
            cost_price=600.00,
            product_quantity=30,
            minimum_stock_level=5,
            category=self.category,
            subcategory=self.subcategory,
            organisation=self.organisor_profile
        )
        
        # Agent için aynı organisation'dan ürün
        self.agent_product = ProductsAndStock.objects.create(
            product_name="Agent Product",
            product_description="Agent's product",
            product_price=599.99,
            cost_price=400.00,
            product_quantity=20,
            minimum_stock_level=3,
            category=self.category,
            subcategory=self.subcategory,
            organisation=self.agent_profile
        )
    
    def test_list_view_anonymous_user(self):
        """Anonim kullanıcı erişim testi"""
        response = self.client.get(reverse('ProductsAndStock:ProductAndStock-list'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_list_view_admin_user(self):
        """Admin kullanıcı erişim testi"""
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('ProductsAndStock:ProductAndStock-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "iPhone 15")
        self.assertContains(response, "Samsung Galaxy")
    
    def test_list_view_organisor_user(self):
        """Organisor kullanıcı erişim testi"""
        self.client.force_login(self.organisor_user)
        response = self.client.get(reverse('ProductsAndStock:ProductAndStock-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "iPhone 15")
        self.assertContains(response, "Samsung Galaxy")
    
    def test_list_view_agent_user(self):
        """Agent kullanıcı erişim testi"""
        self.client.force_login(self.agent_user)
        response = self.client.get(reverse('ProductsAndStock:ProductAndStock-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Agent Product")  # Agent'ın kendi ürünü
    
    def test_list_view_category_filter(self):
        """Kategori filtresi testi"""
        self.client.force_login(self.admin_user)
        response = self.client.get(
            reverse('ProductsAndStock:ProductAndStock-list'),
            {'category': self.category.id}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "iPhone 15")
        self.assertContains(response, "Samsung Galaxy")
    
    def test_list_view_subcategory_filter(self):
        """Alt kategori filtresi testi"""
        self.client.force_login(self.admin_user)
        response = self.client.get(
            reverse('ProductsAndStock:ProductAndStock-list'),
            {'subcategory': self.subcategory.id}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "iPhone 15")
        self.assertContains(response, "Samsung Galaxy")
    
    def test_list_view_context_data(self):
        """Context data testi"""
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('ProductsAndStock:ProductAndStock-list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('total_products', response.context)
        self.assertIn('total_quantity', response.context)
        self.assertIn('total_value', response.context)
        self.assertIn('categories', response.context)
        
        self.assertEqual(response.context['total_products'], 3)  # 3 ürün var
        self.assertEqual(response.context['total_quantity'], 100)  # 50+30+20
        self.assertEqual(response.context['total_value'], 49999.5 + 23999.7 + 11999.8)  # Doğru hesaplama


class TestProductAndStockDetailView(TestCase):
    """ProductAndStockDetailView tests"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        self.admin_user = User.objects.create_user(
            username="admin_views_main",
            email="admin_views_main@example.com",
            password="adminpass123",
            is_superuser=True
        )
        
        self.organisor_user = User.objects.create_user(
            username="organisor_views_main",
            email="organisor_views_main@example.com",
            password="organisorpass123",
            is_organisor=True
        )
        self.organisor_profile, created = UserProfile.objects.get_or_create(
            user=self.organisor_user
        )
        if created:
            self.organisor_profile.save()  # Ensure pk is assigned
        
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
        
        # Stok hareketi ve fiyat geçmişi oluştur
        StockMovement.objects.create(
            product=self.product,
            movement_type='IN',
            quantity_before=40,
            quantity_after=50,
            quantity_change=10,
            reason='Stock replenishment',
            created_by=self.admin_user
        )
        
        PriceHistory.objects.create(
            product=self.product,
            old_price=899.99,
            new_price=999.99,
            price_change=100.0,
            change_type='INCREASE',
            change_reason='Price increase',
            updated_by=self.admin_user
        )
    
    def test_detail_view_anonymous_user(self):
        """Anonim kullanıcı erişim testi"""
        response = self.client.get(
            reverse('ProductsAndStock:ProductAndStock-detail', kwargs={'pk': self.product.pk})
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_detail_view_admin_user(self):
        """Admin kullanıcı erişim testi"""
        self.client.force_login(self.admin_user)
        response = self.client.get(
            reverse('ProductsAndStock:ProductAndStock-detail', kwargs={'pk': self.product.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "iPhone 15")
        self.assertContains(response, "Latest iPhone model")
    
    def test_detail_view_organisor_user(self):
        """Organisor kullanıcı erişim testi"""
        self.client.force_login(self.organisor_user)
        response = self.client.get(
            reverse('ProductsAndStock:ProductAndStock-detail', kwargs={'pk': self.product.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "iPhone 15")
    
    def test_detail_view_context_data(self):
        """Detail view context data testi"""
        self.client.force_login(self.admin_user)
        response = self.client.get(
            reverse('ProductsAndStock:ProductAndStock-detail', kwargs={'pk': self.product.pk})
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('stock_movements', response.context)
        self.assertIn('price_history', response.context)
        
        # Stok hareketleri ve fiyat geçmişi kontrolü
        self.assertEqual(len(response.context['stock_movements']), 2)  # 2 movement var
        self.assertEqual(len(response.context['price_history']), 1)


class TestProductAndStockCreateView(TestCase):
    """ProductAndStockCreateView tests"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        self.admin_user = User.objects.create_user(
            username="admin_views_main",
            email="admin_views_main@example.com",
            password="adminpass123",
            is_superuser=True
        )
        
        self.organisor_user = User.objects.create_user(
            username="organisor_views_main",
            email="organisor_views_main@example.com",
            password="organisorpass123",
            is_organisor=True
        )
        self.organisor_profile, created = UserProfile.objects.get_or_create(
            user=self.organisor_user
        )
        if created:
            self.organisor_profile.save()  # Ensure pk is assigned
        
        self.category = Category.objects.create(name="Electronics")
        self.subcategory = SubCategory.objects.create(
            name="Smartphones",
            category=self.category
        )
    
    def test_create_view_anonymous_user(self):
        """Anonim kullanıcı erişim testi"""
        response = self.client.get(reverse('ProductsAndStock:ProductAndStock-create'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_create_view_get_admin(self):
        """Admin kullanıcı GET isteği testi"""
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('ProductsAndStock:ProductAndStock-create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "form")
    
    def test_create_view_get_organisor(self):
        """Organisor kullanıcı GET isteği testi"""
        self.client.force_login(self.organisor_user)
        response = self.client.get(reverse('ProductsAndStock:ProductAndStock-create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "form")
    
    def test_create_view_post_admin(self):
        """Admin kullanıcı POST isteği testi"""
        self.client.force_login(self.admin_user)
        
        data = {
            'product_name': 'Test Product',
            'product_description': 'Test Description',
            'product_price': 99.99,
            'cost_price': 80.00,
            'product_quantity': 10,
            'minimum_stock_level': 2,
            'category': self.category.id,
            'subcategory': self.subcategory.id,
            'organisation': self.organisor_profile.id,
            'discount_percentage': 0,
            'discount_amount': 0,
        }
        
        response = self.client.post(reverse('ProductsAndStock:ProductAndStock-create'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        # Ürün oluşturuldu mu kontrol et
        self.assertTrue(ProductsAndStock.objects.filter(product_name='Test Product').exists())
    
    def test_create_view_post_organisor(self):
        """Organisor kullanıcı POST isteği testi"""
        self.client.force_login(self.organisor_user)
        
        data = {
            'product_name': 'Test Product 2',
            'product_description': 'Test Description 2',
            'product_price': 149.99,
            'cost_price': 120.00,
            'product_quantity': 20,
            'minimum_stock_level': 5,
            'category': self.category.id,
            'subcategory': self.subcategory.id,
            'discount_percentage': 0,
            'discount_amount': 0,
        }
        
        response = self.client.post(reverse('ProductsAndStock:ProductAndStock-create'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        # Ürün oluşturuldu mu kontrol et
        product = ProductsAndStock.objects.get(product_name='Test Product 2')
        self.assertEqual(product.organisation, self.organisor_profile)
    
    def test_create_view_invalid_data(self):
        """Geçersiz veri ile POST isteği testi"""
        self.client.force_login(self.organisor_user)
        
        data = {
            'product_name': '',  # Boş isim
            'product_description': 'Test Description',
            'product_price': -10,  # Negatif fiyat
            'cost_price': 80.00,
            'product_quantity': 10,
            'minimum_stock_level': 2,
            'category': self.category.id,
            'subcategory': self.subcategory.id,
        }
        
        response = self.client.post(reverse('ProductsAndStock:ProductAndStock-create'), data)
        self.assertEqual(response.status_code, 200)  # Form hataları ile geri döner
        
        # Ürün oluşturulmadı mı kontrol et
        self.assertFalse(ProductsAndStock.objects.filter(product_description='Test Description').exists())


class TestProductAndStockUpdateView(TestCase):
    """ProductAndStockUpdateView tests"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        self.admin_user = User.objects.create_user(
            username="admin_views_main",
            email="admin_views_main@example.com",
            password="adminpass123",
            is_superuser=True
        )
        
        self.organisor_user = User.objects.create_user(
            username="organisor_views_main",
            email="organisor_views_main@example.com",
            password="organisorpass123",
            is_organisor=True
        )
        self.organisor_profile, created = UserProfile.objects.get_or_create(
            user=self.organisor_user
        )
        if created:
            self.organisor_profile.save()  # Ensure pk is assigned
        
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
    
    def test_update_view_anonymous_user(self):
        """Anonim kullanıcı erişim testi"""
        response = self.client.get(
            reverse('ProductsAndStock:ProductAndStock-update', kwargs={'pk': self.product.pk})
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_update_view_get_admin(self):
        """Admin kullanıcı GET isteği testi"""
        self.client.force_login(self.admin_user)
        response = self.client.get(
            reverse('ProductsAndStock:ProductAndStock-update', kwargs={'pk': self.product.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "iPhone 15")
    
    def test_update_view_get_organisor(self):
        """Organisor kullanıcı GET isteği testi"""
        self.client.force_login(self.organisor_user)
        response = self.client.get(
            reverse('ProductsAndStock:ProductAndStock-update', kwargs={'pk': self.product.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "iPhone 15")
    
    def test_update_view_post_admin(self):
        """Admin kullanıcı POST isteği testi"""
        self.client.force_login(self.admin_user)
        
        data = {
            'product_name': 'iPhone 15 Pro',
            'product_description': 'Updated iPhone model',
            'product_price': 1099.99,
            'cost_price': 900.00,
            'product_quantity': 60,
            'minimum_stock_level': 15,
            'category': self.category.id,
            'subcategory': self.subcategory.id,
            'organisation': self.organisor_profile.id,
            'discount_percentage': 0,
            'discount_amount': 0,
        }
        
        response = self.client.post(
            reverse('ProductsAndStock:ProductAndStock-update', kwargs={'pk': self.product.pk}),
            data
        )
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        # Ürün güncellendi mi kontrol et
        updated_product = ProductsAndStock.objects.get(pk=self.product.pk)
        self.assertEqual(updated_product.product_name, 'iPhone 15 Pro')
        self.assertEqual(updated_product.product_price, 1099.99)
    
    def test_update_view_post_organisor(self):
        """Organisor kullanıcı POST isteği testi"""
        self.client.force_login(self.organisor_user)
        
        data = {
            'product_name': 'iPhone 15 Plus',
            'product_description': 'Updated iPhone model',
            'product_price': 1199.99,
            'cost_price': 1000.00,
            'product_quantity': 40,
            'minimum_stock_level': 8,
            'category': self.category.id,
            'subcategory': self.subcategory.id,
            'discount_percentage': 0,
            'discount_amount': 0,
        }
        
        response = self.client.post(
            reverse('ProductsAndStock:ProductAndStock-update', kwargs={'pk': self.product.pk}),
            data
        )
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        # Ürün güncellendi mi kontrol et
        updated_product = ProductsAndStock.objects.get(pk=self.product.pk)
        self.assertEqual(updated_product.product_name, 'iPhone 15 Plus')
        self.assertEqual(updated_product.product_price, 1199.99)


class TestProductAndStockDeleteView(TestCase):
    """ProductAndStockDeleteView tests"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        self.admin_user = User.objects.create_user(
            username="admin_views_main",
            email="admin_views_main@example.com",
            password="adminpass123",
            is_superuser=True
        )
        
        self.organisor_user = User.objects.create_user(
            username="organisor_views_main",
            email="organisor_views_main@example.com",
            password="organisorpass123",
            is_organisor=True
        )
        self.organisor_profile, created = UserProfile.objects.get_or_create(
            user=self.organisor_user
        )
        if created:
            self.organisor_profile.save()  # Ensure pk is assigned
        
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
    
    def test_delete_view_anonymous_user(self):
        """Anonim kullanıcı erişim testi"""
        response = self.client.get(
            reverse('ProductsAndStock:ProductAndStock-delete', kwargs={'pk': self.product.pk})
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_delete_view_get_admin(self):
        """Admin kullanıcı GET isteği testi"""
        self.client.force_login(self.admin_user)
        response = self.client.get(
            reverse('ProductsAndStock:ProductAndStock-delete', kwargs={'pk': self.product.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "iPhone 15")
    
    def test_delete_view_post_admin(self):
        """Admin kullanıcı POST isteği testi"""
        self.client.force_login(self.admin_user)
        
        response = self.client.post(
            reverse('ProductsAndStock:ProductAndStock-delete', kwargs={'pk': self.product.pk})
        )
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        # Ürün silindi mi kontrol et
        self.assertFalse(ProductsAndStock.objects.filter(pk=self.product.pk).exists())
    
    def test_delete_view_post_organisor(self):
        """Organisor kullanıcı POST isteği testi"""
        self.client.force_login(self.organisor_user)
        
        response = self.client.post(
            reverse('ProductsAndStock:ProductAndStock-delete', kwargs={'pk': self.product.pk})
        )
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        # Ürün silindi mi kontrol et
        self.assertFalse(ProductsAndStock.objects.filter(pk=self.product.pk).exists())


class TestGetSubcategoriesView(TestCase):
    """get_subcategories view tests"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        self.category = Category.objects.create(name="Electronics")
        self.subcategory1 = SubCategory.objects.create(
            name="Smartphones",
            category=self.category
        )
        self.subcategory2 = SubCategory.objects.create(
            name="Laptops",
            category=self.category
        )
    
    def test_get_subcategories_valid_category(self):
        """Geçerli kategori ID ile test"""
        response = self.client.get(
            reverse('ProductsAndStock:get-subcategories'),
            {'category_id': self.category.id}
        )
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('subcategories', data)
        self.assertEqual(len(data['subcategories']), 2)
        
        subcategory_names = [sub['name'] for sub in data['subcategories']]
        self.assertIn('Smartphones', subcategory_names)
        self.assertIn('Laptops', subcategory_names)
    
    def test_get_subcategories_invalid_category(self):
        """Geçersiz kategori ID ile test"""
        response = self.client.get(
            reverse('ProductsAndStock:get-subcategories'),
            {'category_id': 'invalid'}
        )
        self.assertEqual(response.status_code, 400)
        
        data = response.json()
        self.assertIn('error', data)
    
    def test_get_subcategories_no_category(self):
        """Kategori ID olmadan test"""
        response = self.client.get(reverse('ProductsAndStock:get-subcategories'))
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('subcategories', data)
        self.assertEqual(len(data['subcategories']), 0)


class TestBulkPriceUpdateView(TestCase):
    """BulkPriceUpdateView tests"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        self.admin_user = User.objects.create_user(
            username="admin_views_main",
            email="admin_views_main@example.com",
            password="adminpass123",
            is_superuser=True
        )
        
        self.organisor_user = User.objects.create_user(
            username="organisor_views_main",
            email="organisor_views_main@example.com",
            password="organisorpass123",
            is_organisor=True
        )
        self.organisor_profile, created = UserProfile.objects.get_or_create(
            user=self.organisor_user
        )
        if created:
            self.organisor_profile.save()  # Ensure pk is assigned
        
        self.category = Category.objects.create(name="Electronics")
        self.subcategory = SubCategory.objects.create(
            name="Smartphones",
            category=self.category
        )
        
        # Test ürünleri oluştur
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
            product_description="Android smartphone",
            product_price=799.99,
            cost_price=600.00,
            product_quantity=30,
            minimum_stock_level=5,
            category=self.category,
            subcategory=self.subcategory,
            organisation=self.organisor_profile
        )
    
    def test_bulk_price_update_view_anonymous_user(self):
        """Anonim kullanıcı erişim testi"""
        response = self.client.get(reverse('ProductsAndStock:bulk-price-update'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_bulk_price_update_view_get_admin(self):
        """Admin kullanıcı GET isteği testi"""
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('ProductsAndStock:bulk-price-update'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "form")
    
    def test_bulk_price_update_percentage_increase(self):
        """Yüzde artış ile toplu fiyat güncelleme testi"""
        self.client.force_login(self.admin_user)
        
        data = {
            'update_type': 'PERCENTAGE_INCREASE',
            'category_filter': 'ALL',
            'percentage_increase': 10.0,
            'reason': 'Market price increase'
        }
        
        response = self.client.post(reverse('ProductsAndStock:bulk-price-update'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        # Fiyatlar güncellendi mi kontrol et
        updated_product1 = ProductsAndStock.objects.get(pk=self.product1.pk)
        updated_product2 = ProductsAndStock.objects.get(pk=self.product2.pk)
        
        expected_price1 = 999.99 * 1.10
        expected_price2 = 799.99 * 1.10
        
        self.assertAlmostEqual(updated_product1.product_price, expected_price1, places=2)
        self.assertAlmostEqual(updated_product2.product_price, expected_price2, places=2)
        
        # Fiyat geçmişi oluşturuldu mu kontrol et
        self.assertTrue(PriceHistory.objects.filter(product=self.product1).exists())
        self.assertTrue(PriceHistory.objects.filter(product=self.product2).exists())
    
    def test_bulk_price_update_fixed_amount_increase(self):
        """Sabit miktar artış ile toplu fiyat güncelleme testi"""
        self.client.force_login(self.admin_user)
        
        data = {
            'update_type': 'FIXED_AMOUNT_INCREASE',
            'category_filter': 'ALL',
            'fixed_amount_increase': 50.0,
            'reason': 'Fixed price increase'
        }
        
        response = self.client.post(reverse('ProductsAndStock:bulk-price-update'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        # Fiyatlar güncellendi mi kontrol et
        updated_product1 = ProductsAndStock.objects.get(pk=self.product1.pk)
        updated_product2 = ProductsAndStock.objects.get(pk=self.product2.pk)
        
        self.assertEqual(updated_product1.product_price, 1049.99)
        self.assertEqual(updated_product2.product_price, 849.99)
    
    def test_bulk_price_update_set_price(self):
        """Yeni fiyat belirleme ile toplu fiyat güncelleme testi"""
        self.client.force_login(self.admin_user)
        
        data = {
            'update_type': 'SET_PRICE',
            'category_filter': 'ALL',
            'new_price': 500.0,
            'reason': 'Set new price'
        }
        
        response = self.client.post(reverse('ProductsAndStock:bulk-price-update'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        # Fiyatlar güncellendi mi kontrol et
        updated_product1 = ProductsAndStock.objects.get(pk=self.product1.pk)
        updated_product2 = ProductsAndStock.objects.get(pk=self.product2.pk)
        
        self.assertEqual(updated_product1.product_price, 500.0)
        self.assertEqual(updated_product2.product_price, 500.0)
    
    def test_bulk_price_update_category_filter(self):
        """Kategori filtresi ile toplu fiyat güncelleme testi"""
        self.client.force_login(self.admin_user)
        
        data = {
            'update_type': 'PERCENTAGE_INCREASE',
            'category_filter': 'CATEGORY',
            'category': self.category.id,
            'percentage_increase': 5.0,
            'reason': 'Category price increase'
        }
        
        response = self.client.post(reverse('ProductsAndStock:bulk-price-update'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        # Sadece seçili kategorideki ürünler güncellendi mi kontrol et
        updated_product1 = ProductsAndStock.objects.get(pk=self.product1.pk)
        updated_product2 = ProductsAndStock.objects.get(pk=self.product2.pk)
        
        expected_price1 = 999.99 * 1.05
        expected_price2 = 799.99 * 1.05
        
        self.assertAlmostEqual(updated_product1.product_price, expected_price1, places=2)
        self.assertAlmostEqual(updated_product2.product_price, expected_price2, places=2)


class TestSalesDashboardView(TestCase):
    """SalesDashboardView tests"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        self.admin_user = User.objects.create_user(
            username="admin_views_main",
            email="admin_views_main@example.com",
            password="adminpass123",
            is_superuser=True
        )
        
        self.organisor_user = User.objects.create_user(
            username="organisor_views_main",
            email="organisor_views_main@example.com",
            password="organisorpass123",
            is_organisor=True
        )
        self.organisor_profile, created = UserProfile.objects.get_or_create(
            user=self.organisor_user
        )
        if created:
            self.organisor_profile.save()  # Ensure pk is assigned
        
        self.category = Category.objects.create(name="Electronics")
        self.subcategory = SubCategory.objects.create(
            name="Smartphones",
            category=self.category
        )
        
        # Test ürünleri oluştur
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
            product_description="Android smartphone",
            product_price=799.99,
            cost_price=600.00,
            product_quantity=5,  # Low stock
            minimum_stock_level=10,
            category=self.category,
            subcategory=self.subcategory,
            organisation=self.organisor_profile
        )
        
        # Stok uyarısı oluştur
        StockAlert.objects.create(
            product=self.product2,
            alert_type='LOW_STOCK',
            severity='HIGH',
            message='Stock level is low',
            is_resolved=False
        )
        
        # Stok önerisi oluştur
        StockRecommendation.objects.create(
            product=self.product2,
            recommendation_type='RESTOCK',
            suggested_quantity=30,
            reason='Low stock level',
            confidence_score=85.0,
            is_applied=False
        )
    
    def test_sales_dashboard_view_anonymous_user(self):
        """Anonim kullanıcı erişim testi"""
        response = self.client.get(reverse('ProductsAndStock:sales-dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_sales_dashboard_view_admin_user(self):
        """Admin kullanıcı erişim testi"""
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('ProductsAndStock:sales-dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dashboard")
    
    def test_sales_dashboard_view_organisor_user(self):
        """Organisor kullanıcı erişim testi"""
        self.client.force_login(self.organisor_user)
        response = self.client.get(reverse('ProductsAndStock:sales-dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dashboard")
    
    def test_sales_dashboard_context_data(self):
        """Dashboard context data testi"""
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('ProductsAndStock:sales-dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('total_products', response.context)
        self.assertIn('total_value', response.context)
        self.assertIn('total_profit', response.context)
        self.assertIn('low_stock_products', response.context)
        self.assertIn('out_of_stock_products', response.context)
        self.assertIn('in_stock_products', response.context)
        self.assertIn('top_selling_products', response.context)
        self.assertIn('recent_alerts', response.context)
        self.assertIn('stock_recommendations', response.context)
        self.assertIn('critical_alerts_count', response.context)
        self.assertIn('products_with_alerts', response.context)
        
        # Değerleri kontrol et
        self.assertEqual(response.context['total_products'], 2)
        self.assertEqual(response.context['low_stock_products'], 1)
        self.assertEqual(response.context['out_of_stock_products'], 0)
        self.assertEqual(response.context['in_stock_products'], 1)


if __name__ == "__main__":
    print("ProductsAndStock Viewları Testleri Başlatılıyor...")
    print("=" * 60)
    
    # Test çalıştırma
    import unittest
    unittest.main()
