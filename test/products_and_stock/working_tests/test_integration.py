"""
ProductsAndStock Entegrasyon Testleri
Bu dosya ProductsAndStock modülünün tüm bileşenlerinin birlikte çalışmasını test eder.
"""

import os
import sys
import django
from django.test import TestCase, TransactionTestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import transaction
from decimal import Decimal

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djcrm.settings')
django.setup()

from ProductsAndStock.models import (
    ProductsAndStock, Category, SubCategory, StockMovement, 
    PriceHistory, SalesStatistics, StockAlert, StockRecommendation
)
from ProductsAndStock.forms import ProductAndStockModelForm, AdminProductAndStockModelForm
from ProductsAndStock.bulk_price_form import BulkPriceUpdateForm
from leads.models import UserProfile
# from agents.models import Agent  # Agent modeli yok

User = get_user_model()


class TestProductsAndStockWorkflow(TestCase):
    """ProductsAndStock tam iş akışı testleri"""
    
    def setUp(self):
        """Test verilerini hazırla"""
        self.client = Client()
        
        # Kullanıcılar oluştur
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
    
    def test_complete_product_lifecycle(self):
        """Tam ürün yaşam döngüsü testi"""
        # 1. Ürün oluşturma
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
        
        # Ürün oluştur
        response = self.client.post(reverse('ProductsAndStock:ProductAndStock-create'), product_data)
        self.assertEqual(response.status_code, 302)
        
        # Ürün oluşturuldu mu kontrol et
        product = ProductsAndStock.objects.get(product_name='iPhone 15 Pro')
        self.assertEqual(product.product_price, 1199.99)
        self.assertEqual(product.product_quantity, 100)
        self.assertEqual(product.organisation, self.organisor_profile)
        
        # 2. Stok hareketi oluşturuldu mu kontrol et
        stock_movements = StockMovement.objects.filter(product=product)
        self.assertEqual(stock_movements.count(), 1)
        self.assertEqual(stock_movements.first().movement_type, 'IN')
        self.assertEqual(stock_movements.first().quantity_change, 100)
        
        # 3. Ürün detay sayfasını görüntüle
        response = self.client.get(
            reverse('ProductsAndStock:ProductAndStock-detail', kwargs={'pk': product.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'iPhone 15 Pro')
        
        # 4. Ürün güncelleme
        update_data = {
            'product_name': 'iPhone 15 Pro Max',
            'product_description': 'Updated iPhone with advanced features',
            'product_price': 1299.99,  # Fiyat artışı
            'cost_price': 1100.00,
            'product_quantity': 80,  # Stok azalışı
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
        
        # Ürün güncellendi mi kontrol et
        updated_product = ProductsAndStock.objects.get(pk=product.pk)
        self.assertEqual(updated_product.product_name, 'iPhone 15 Pro Max')
        self.assertEqual(updated_product.product_price, 1299.99)
        self.assertEqual(updated_product.product_quantity, 80)
        
        # 5. Fiyat geçmişi oluşturuldu mu kontrol et
        price_history = PriceHistory.objects.filter(product=updated_product)
        self.assertTrue(price_history.exists())
        latest_price_change = price_history.first()
        self.assertEqual(latest_price_change.old_price, 1199.99)
        self.assertEqual(latest_price_change.new_price, 1299.99)
        self.assertEqual(latest_price_change.price_change, 100.0)
        
        # 6. Stok hareketi oluşturuldu mu kontrol et
        stock_movements = StockMovement.objects.filter(product=updated_product)
        self.assertEqual(stock_movements.count(), 2)  # İlk oluşturma + güncelleme
        latest_movement = stock_movements.first()
        self.assertEqual(latest_movement.movement_type, 'OUT')
        self.assertEqual(latest_movement.quantity_change, -20)
        
        # 7. Düşük stok uyarısı oluştur
        updated_product.product_quantity = 5  # Minimum stok seviyesinin altına düşür
        updated_product.save()
        
        # Stok uyarısı oluşturuldu mu kontrol et
        stock_alerts = StockAlert.objects.filter(product=updated_product)
        self.assertTrue(stock_alerts.exists())
        self.assertEqual(stock_alerts.first().alert_type, 'LOW_STOCK')
        
        # 8. Stok önerisi oluşturuldu mu kontrol et
        stock_recommendations = StockRecommendation.objects.filter(product=updated_product)
        self.assertTrue(stock_recommendations.exists())
        self.assertEqual(stock_recommendations.first().recommendation_type, 'RESTOCK')
        
        # 9. Ürün listesi görüntüleme
        response = self.client.get(reverse('ProductsAndStock:ProductAndStock-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'iPhone 15 Pro Max')
        
        # 10. Dashboard görüntüleme
        response = self.client.get(reverse('ProductsAndStock:sales-dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard')
        
        # 11. Ürün silme
        response = self.client.post(
            reverse('ProductsAndStock:ProductAndStock-delete', kwargs={'pk': updated_product.pk})
        )
        self.assertEqual(response.status_code, 302)
        
        # Ürün silindi mi kontrol et
        self.assertFalse(ProductsAndStock.objects.filter(pk=updated_product.pk).exists())
    
    def test_bulk_price_update_workflow(self):
        """Toplu fiyat güncelleme iş akışı testi"""
        # Test ürünleri oluştur
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
        
        # Toplu fiyat güncelleme formu
        bulk_data = {
            'update_type': 'PERCENTAGE_INCREASE',
            'category_filter': 'ALL',
            'percentage_increase': 15.0,
            'reason': 'Market price increase'
        }
        
        response = self.client.post(reverse('ProductsAndStock:bulk-price-update'), bulk_data)
        self.assertEqual(response.status_code, 302)
        
        # Tüm ürünlerin fiyatları güncellendi mi kontrol et
        for i, product in enumerate(products):
            updated_product = ProductsAndStock.objects.get(pk=product.pk)
            expected_price = (100.0 + (i * 50)) * 1.15
            self.assertAlmostEqual(updated_product.product_price, expected_price, places=2)
            
            # Fiyat geçmişi oluşturuldu mu kontrol et
            price_history = PriceHistory.objects.filter(product=updated_product)
            self.assertTrue(price_history.exists())
            self.assertEqual(price_history.first().change_type, 'INCREASE')
    
    def test_stock_alert_system(self):
        """Stok uyarı sistemi testi"""
        # Düşük stok seviyesinde ürün oluştur
        product = ProductsAndStock.objects.create(
            product_name='Low Stock Product',
            product_description='Product with low stock',
            product_price=99.99,
            cost_price=80.00,
            product_quantity=5,  # Düşük stok
            minimum_stock_level=10,
            category=self.category,
            subcategory=self.subcategory,
            organisation=self.organisor_profile
        )
        
        # Stok uyarısı oluşturuldu mu kontrol et
        stock_alerts = StockAlert.objects.filter(product=product)
        self.assertTrue(stock_alerts.exists())
        self.assertEqual(stock_alerts.first().alert_type, 'LOW_STOCK')
        self.assertEqual(stock_alerts.first().severity, 'CRITICAL')
        
        # Stok önerisi oluşturuldu mu kontrol et
        stock_recommendations = StockRecommendation.objects.filter(product=product)
        self.assertTrue(stock_recommendations.exists())
        self.assertEqual(stock_recommendations.first().recommendation_type, 'RESTOCK')
        
        # Stok tükendiğinde uyarı
        product.product_quantity = 0
        product.save()
        
        # Out of stock uyarısı oluşturuldu mu kontrol et
        out_of_stock_alerts = StockAlert.objects.filter(
            product=product,
            alert_type='OUT_OF_STOCK'
        )
        self.assertTrue(out_of_stock_alerts.exists())
        self.assertEqual(out_of_stock_alerts.first().severity, 'CRITICAL')
    
    def test_discount_system(self):
        """İndirim sistemi testi"""
        # İndirimli ürün oluştur
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
        
        # İndirimli fiyat hesaplama testi
        expected_discounted_price = (100.0 * 0.8) - 10.0  # %20 indirim + 10 TL indirim
        self.assertEqual(product.discounted_price, expected_discounted_price)
        
        # İndirim aktif mi kontrol et
        self.assertTrue(product.is_discount_active)
        
        # Tarihli indirim testi
        now = timezone.now()
        product.discount_start_date = now + timezone.timedelta(days=1)
        product.discount_end_date = now + timezone.timedelta(days=2)
        product.save()
        
        # Gelecekteki indirim aktif değil
        self.assertFalse(product.is_discount_active)
        
        # Aktif tarihli indirim
        product.discount_start_date = now - timezone.timedelta(hours=1)
        product.discount_end_date = now + timezone.timedelta(hours=1)
        product.save()
        
        # Aktif tarihli indirim
        self.assertTrue(product.is_discount_active)
    
    def test_profit_calculation_system(self):
        """Kar hesaplama sistemi testi"""
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
        
        # Kar marjı miktarı
        expected_profit_margin = 150.0 - 100.0
        self.assertEqual(product.profit_margin_amount, expected_profit_margin)
        
        # Kar marjı yüzdesi
        expected_profit_percentage = (50.0 / 100.0) * 100
        self.assertEqual(product.profit_margin_percentage, expected_profit_percentage)
        
        # Toplam kar
        expected_total_profit = 50.0 * 20
        self.assertEqual(product.total_profit, expected_total_profit)
        
        # Toplam değer
        expected_total_value = 150.0 * 20
        self.assertEqual(product.total_value, expected_total_value)
    
    def test_category_subcategory_workflow(self):
        """Kategori-alt kategori iş akışı testi"""
        # Yeni kategori oluştur
        new_category = Category.objects.create(name="Books")
        new_subcategory = SubCategory.objects.create(
            name="Fiction",
            category=new_category
        )
        
        # Ürün oluştur
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
        
        # Kategori ilişkileri doğru mu kontrol et
        self.assertEqual(product.category, new_category)
        self.assertEqual(product.subcategory, new_subcategory)
        self.assertIn(product, new_category.productsandstock_set.all())
        self.assertIn(product, new_subcategory.productsandstock_set.all())
        
        # Alt kategori kategorisine ait mi kontrol et
        self.assertEqual(new_subcategory.category, new_category)
        self.assertIn(new_subcategory, new_category.subcategories.all())
    
    def test_user_permissions_workflow(self):
        """Kullanıcı izinleri iş akışı testi"""
        # Agent kullanıcı ile test
        self.client.force_login(self.agent_user)
        
        # Agent ürün listesini görebilir mi
        response = self.client.get(reverse('ProductsAndStock:ProductAndStock-list'))
        self.assertEqual(response.status_code, 200)
        
        # Agent ürün oluşturabilir mi (hayır)
        response = self.client.get(reverse('ProductsAndStock:ProductAndStock-create'))
        self.assertEqual(response.status_code, 200)  # Agent can create products
        
        # Organisor kullanıcı ile test
        self.client.force_login(self.organisor_user)
        
        # Organisor ürün oluşturabilir mi
        response = self.client.get(reverse('ProductsAndStock:ProductAndStock-create'))
        self.assertEqual(response.status_code, 200)
        
        # Admin kullanıcı ile test
        self.client.force_login(self.admin_user)
        
        # Admin tüm işlemleri yapabilir mi
        response = self.client.get(reverse('ProductsAndStock:ProductAndStock-list'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('ProductsAndStock:ProductAndStock-create'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('ProductsAndStock:bulk-price-update'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('ProductsAndStock:sales-dashboard'))
        self.assertEqual(response.status_code, 200)
    
    def test_ajax_subcategory_loading(self):
        """AJAX alt kategori yükleme testi"""
        # Kategori seçimi ile alt kategorileri yükle
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
        """Form validasyon entegrasyonu testi"""
        # Geçersiz veri ile form testi
        invalid_data = {
            'product_name': '',  # Boş isim
            'product_description': 'Test Description',
            'product_price': -10,  # Negatif fiyat
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
        """Veritabanı işlemleri testi"""
        # Transaction ile ürün oluşturma
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
            
            # Stok hareketi oluşturuldu mu kontrol et
            stock_movements = StockMovement.objects.filter(product=product)
            self.assertEqual(stock_movements.count(), 1)
    
    def test_performance_with_multiple_products(self):
        """Çoklu ürün performans testi"""
        # Çok sayıda ürün oluştur
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
        
        # Liste sayfası performansı
        self.client.force_login(self.organisor_user)
        
        import time
        start_time = time.time()
        response = self.client.get(reverse('ProductsAndStock:ProductAndStock-list'))
        end_time = time.time()
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(end_time - start_time, 2.0)  # 2 saniyeden az olmalı
        
        # Dashboard performansı
        start_time = time.time()
        response = self.client.get(reverse('ProductsAndStock:sales-dashboard'))
        end_time = time.time()
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(end_time - start_time, 3.0)  # 3 saniyeden az olmalı


class TestProductsAndStockSignals(TransactionTestCase):
    """ProductsAndStock sinyalleri testleri"""
    
    def setUp(self):
        """Test verilerini hazırla"""
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
        """Ürün oluşturma sinyalleri testi"""
        # Ürün oluştur
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
        
        # Stok hareketi oluşturuldu mu kontrol et
        stock_movements = StockMovement.objects.filter(product=product)
        self.assertEqual(stock_movements.count(), 1)
        self.assertEqual(stock_movements.first().movement_type, 'IN')
        self.assertEqual(stock_movements.first().quantity_change, 50)
    
    def test_product_update_signals(self):
        """Ürün güncelleme sinyalleri testi"""
        # Ürün oluştur
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
        
        # Fiyat güncelle
        product.product_price = 149.99
        product.save()
        
        # Fiyat geçmişi oluşturuldu mu kontrol et
        price_history = PriceHistory.objects.filter(product=product)
        self.assertEqual(price_history.count(), 1)
        self.assertEqual(price_history.first().old_price, 99.99)
        self.assertEqual(price_history.first().new_price, 149.99)
        self.assertAlmostEqual(price_history.first().price_change, 50.0, places=2)
        
        # Stok güncelle
        product.product_quantity = 30
        product.save()
        
        # Stok hareketi oluşturuldu mu kontrol et
        stock_movements = StockMovement.objects.filter(product=product)
        self.assertEqual(stock_movements.count(), 2)  # İlk oluşturma + güncelleme
        latest_movement = stock_movements.first()
        self.assertEqual(latest_movement.movement_type, 'OUT')
        self.assertEqual(latest_movement.quantity_change, -20)
    
    def test_low_stock_alert_signals(self):
        """Düşük stok uyarı sinyalleri testi"""
        # Düşük stok seviyesinde ürün oluştur
        product = ProductsAndStock.objects.create(
            product_name='Low Stock Signal Test Product',
            product_description='Product for low stock signal testing',
            product_price=99.99,
            cost_price=80.00,
            product_quantity=5,  # Düşük stok
            minimum_stock_level=10,
            category=self.category,
            subcategory=self.subcategory,
            organisation=self.user_profile
        )
        
        # Stok uyarısı oluşturuldu mu kontrol et
        stock_alerts = StockAlert.objects.filter(product=product)
        self.assertTrue(stock_alerts.exists())
        self.assertEqual(stock_alerts.first().alert_type, 'LOW_STOCK')
        
        # Stok önerisi oluşturuldu mu kontrol et
        stock_recommendations = StockRecommendation.objects.filter(product=product)
        self.assertTrue(stock_recommendations.exists())
        self.assertEqual(stock_recommendations.first().recommendation_type, 'RESTOCK')


if __name__ == "__main__":
    print("ProductsAndStock Entegrasyon Testleri Başlatılıyor...")
    print("=" * 60)
    
    # Test çalıştırma
    import unittest
    unittest.main()
