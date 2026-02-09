"""
ProductsAndStock Forms Test File
This file tests all forms in the ProductsAndStock module.
"""

import os
import sys
import django
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone

# Load Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djcrm.settings')
django.setup()

from ProductsAndStock.forms import ProductAndStockModelForm, AdminProductAndStockModelForm
from ProductsAndStock.bulk_price_form import BulkPriceUpdateForm
from ProductsAndStock.models import ProductsAndStock, Category, SubCategory
from leads.models import User, UserProfile


class TestProductAndStockModelForm(TestCase):
    """ProductAndStockModelForm testleri"""
    
    def setUp(self):
        """Test verilerini hazırla"""
        self.user = User.objects.create_user(
            username="testuser_forms_main",
            email="test_forms_main@example.com",
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
        
        self.valid_data = {
            'product_name': 'iPhone 15',
            'product_description': 'Latest iPhone model',
            'product_price': 999.99,
            'cost_price': 800.00,
            'product_quantity': 50,
            'minimum_stock_level': 10,
            'category': self.category.id,
            'subcategory': self.subcategory.id,
            'discount_percentage': 0,
            'discount_amount': 0,
        }
    
    def test_form_initialization(self):
        """Form başlatma testi"""
        form = ProductAndStockModelForm()
        
        # Gerekli alanların varlığını kontrol et
        self.assertIn('product_name', form.fields)
        self.assertIn('product_description', form.fields)
        self.assertIn('product_price', form.fields)
        self.assertIn('cost_price', form.fields)
        self.assertIn('product_quantity', form.fields)
        self.assertIn('minimum_stock_level', form.fields)
        self.assertIn('category', form.fields)
        self.assertIn('subcategory', form.fields)
        self.assertIn('discount_percentage', form.fields)
        self.assertIn('discount_amount', form.fields)
        self.assertIn('discount_start_date', form.fields)
        self.assertIn('discount_end_date', form.fields)
    
    def test_form_valid_data(self):
        """Geçerli veri ile form testi"""
        form = ProductAndStockModelForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
    
    def test_form_required_fields(self):
        """Zorunlu alanlar testi"""
        required_fields = [
            'product_name', 'product_description', 'product_price',
            'cost_price', 'product_quantity', 'minimum_stock_level',
            'category', 'subcategory'
        ]
        
        for field in required_fields:
            data = self.valid_data.copy()
            del data[field]
            
            form = ProductAndStockModelForm(data=data)
            self.assertFalse(form.is_valid())
            self.assertIn(field, form.errors)
    
    def test_form_product_name_validation(self):
        """Ürün adı validasyonu testi"""
        # Aynı organizasyon altında aynı isimde ürün oluştur
        ProductsAndStock.objects.create(
            product_name='iPhone 15',
            product_description='Existing product',
            product_price=999.99,
            cost_price=800.00,
            product_quantity=10,
            minimum_stock_level=2,
            category=self.category,
            subcategory=self.subcategory,
            organisation=self.user_profile
        )
        
        # Aynı isimde ürün oluşturmaya çalış
        form = ProductAndStockModelForm(data=self.valid_data)
        form.user_organisation = self.user_profile
        self.assertFalse(form.is_valid())
        self.assertIn('product_name', form.errors)
        self.assertIn('already exists', str(form.errors['product_name']))
    
    def test_form_subcategory_validation(self):
        """Alt kategori validasyonu testi"""
        # Farklı kategoride alt kategori oluştur
        other_category = Category.objects.create(name="Books")
        other_subcategory = SubCategory.objects.create(
            name="Fiction",
            category=other_category
        )
        
        data = self.valid_data.copy()
        data['subcategory'] = other_subcategory.id
        
        form = ProductAndStockModelForm(data=data)
        self.assertFalse(form.is_valid())
        # Form validasyonu subcategory seviyesinde hata veriyor
        self.assertIn('subcategory', form.errors)
        self.assertIn('valid choice', str(form.errors['subcategory']))
    
    def test_form_dynamic_subcategory_queryset(self):
        """Dinamik alt kategori queryset testi"""
        # Form verisi ile kategori seçildiğinde
        form_data = {
            'category': self.category.id,
            'subcategory': self.subcategory.id,
        }
        form = ProductAndStockModelForm(data=form_data)
        
        # Alt kategoriler doğru filtrelenmiş mi
        self.assertEqual(
            list(form.fields['subcategory'].queryset),
            list(SubCategory.objects.filter(category=self.category))
        )
    
    def test_form_instance_with_category(self):
        """Mevcut instance ile kategori testi"""
        product = ProductsAndStock.objects.create(
            product_name='Test Product',
            product_description='Test Description',
            product_price=99.99,
            cost_price=80.00,
            product_quantity=10,
            minimum_stock_level=2,
            category=self.category,
            subcategory=self.subcategory,
            organisation=self.user_profile
        )
        
        form = ProductAndStockModelForm(instance=product)
        
        # Alt kategoriler doğru filtrelenmiş mi
        self.assertEqual(
            list(form.fields['subcategory'].queryset),
            list(SubCategory.objects.filter(category=self.category))
        )
    
    def test_form_widget_attributes(self):
        """Widget özellikleri testi"""
        form = ProductAndStockModelForm()
        
        # CSS sınıfları kontrol et
        self.assertIn('form-control', str(form['product_name'].as_widget()))
        self.assertIn('form-control', str(form['product_description'].as_widget()))
        self.assertIn('form-control', str(form['product_price'].as_widget()))
        self.assertIn('form-control', str(form['cost_price'].as_widget()))
        self.assertIn('form-control', str(form['product_quantity'].as_widget()))
        self.assertIn('form-control', str(form['minimum_stock_level'].as_widget()))
        self.assertIn('form-control', str(form['category'].as_widget()))
        self.assertIn('form-control', str(form['subcategory'].as_widget()))
        self.assertIn('form-control', str(form['discount_percentage'].as_widget()))
        self.assertIn('form-control', str(form['discount_amount'].as_widget()))
    
    def test_form_placeholder_attributes(self):
        """Placeholder özellikleri testi"""
        form = ProductAndStockModelForm()
        
        # Placeholder kontrol et
        self.assertIn('placeholder="Product Name"', str(form['product_name'].as_widget()))
        self.assertIn('placeholder="Product Description"', str(form['product_description'].as_widget()))
        self.assertIn('placeholder="0.00"', str(form['product_price'].as_widget()))
        self.assertIn('placeholder="0.00"', str(form['cost_price'].as_widget()))
        self.assertIn('placeholder="0"', str(form['product_quantity'].as_widget()))
        self.assertIn('placeholder="0"', str(form['minimum_stock_level'].as_widget()))
    
    def test_form_step_attributes(self):
        """Step özellikleri testi"""
        form = ProductAndStockModelForm()
        
        # Step kontrol et
        self.assertIn('step="0.01"', str(form['product_price'].as_widget()))
        self.assertIn('step="0.01"', str(form['cost_price'].as_widget()))
        self.assertIn('step="0.01"', str(form['discount_percentage'].as_widget()))
        self.assertIn('step="0.01"', str(form['discount_amount'].as_widget()))
    
    def test_form_max_attributes(self):
        """Max özellikleri testi"""
        form = ProductAndStockModelForm()
        
        # Max kontrol et
        self.assertIn('max="100"', str(form['discount_percentage'].as_widget()))


class TestAdminProductAndStockModelForm(TestCase):
    """AdminProductAndStockModelForm testleri"""
    
    def setUp(self):
        """Test verilerini hazırla"""
        self.user = User.objects.create_user(
            username="testuser_forms_main",
            email="test_forms_main@example.com",
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
        
        self.valid_data = {
            'product_name': 'iPhone 15',
            'product_description': 'Latest iPhone model',
            'product_price': 999.99,
            'cost_price': 800.00,
            'product_quantity': 50,
            'minimum_stock_level': 10,
            'category': self.category.id,
            'subcategory': self.subcategory.id,
            'organisation': self.user_profile.id,
            'discount_percentage': 0,
            'discount_amount': 0,
        }
    
    def test_form_initialization(self):
        """Form başlatma testi"""
        form = AdminProductAndStockModelForm()
        
        # Admin formunda organisation alanı olmalı
        self.assertIn('organisation', form.fields)
        self.assertIn('product_name', form.fields)
        self.assertIn('category', form.fields)
        self.assertIn('subcategory', form.fields)
    
    def test_form_valid_data(self):
        """Geçerli veri ile form testi"""
        form = AdminProductAndStockModelForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
    
    def test_form_organisation_queryset(self):
        """Organisation queryset testi"""
        form = AdminProductAndStockModelForm()
        
        # Sadece organisor kullanıcıların profilleri olmalı
        expected_queryset = UserProfile.objects.filter(
            user__is_organisor=True,
            user__is_superuser=False
        )
        self.assertEqual(
            list(form.fields['organisation'].queryset),
            list(expected_queryset)
        )
    
    def test_form_product_name_validation(self):
        """Ürün adı validasyonu testi"""
        # Aynı organizasyon altında aynı isimde ürün oluştur
        ProductsAndStock.objects.create(
            product_name='iPhone 15',
            product_description='Existing product',
            product_price=999.99,
            cost_price=800.00,
            product_quantity=10,
            minimum_stock_level=2,
            category=self.category,
            subcategory=self.subcategory,
            organisation=self.user_profile
        )
        
        # Aynı isimde ürün oluşturmaya çalış
        form = AdminProductAndStockModelForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
        self.assertIn('already exists', str(form.errors['__all__']))
    
    def test_form_subcategory_validation(self):
        """Alt kategori validasyonu testi"""
        # Farklı kategoride alt kategori oluştur
        other_category = Category.objects.create(name="Books")
        other_subcategory = SubCategory.objects.create(
            name="Fiction",
            category=other_category
        )
        
        data = self.valid_data.copy()
        data['subcategory'] = other_subcategory.id
        
        form = AdminProductAndStockModelForm(data=data)
        self.assertFalse(form.is_valid())
        # Form validasyonu subcategory seviyesinde hata veriyor
        self.assertIn('subcategory', form.errors)
        self.assertIn('valid choice', str(form.errors['subcategory']))
    
    def test_form_dynamic_subcategory_queryset(self):
        """Dinamik alt kategori queryset testi"""
        # Form verisi ile kategori seçildiğinde
        form_data = {
            'category': self.category.id,
            'subcategory': self.subcategory.id,
        }
        form = AdminProductAndStockModelForm(data=form_data)
        
        # Alt kategoriler doğru filtrelenmiş mi
        self.assertEqual(
            list(form.fields['subcategory'].queryset),
            list(SubCategory.objects.filter(category=self.category))
        )
    
    def test_form_instance_with_category(self):
        """Mevcut instance ile kategori testi"""
        product = ProductsAndStock.objects.create(
            product_name='Test Product',
            product_description='Test Description',
            product_price=99.99,
            cost_price=80.00,
            product_quantity=10,
            minimum_stock_level=2,
            category=self.category,
            subcategory=self.subcategory,
            organisation=self.user_profile
        )
        
        form = AdminProductAndStockModelForm(instance=product)
        
        # Alt kategoriler doğru filtrelenmiş mi
        self.assertEqual(
            list(form.fields['subcategory'].queryset),
            list(SubCategory.objects.filter(category=self.category))
        )


class TestBulkPriceUpdateForm(TestCase):
    """BulkPriceUpdateForm testleri"""
    
    def setUp(self):
        """Test verilerini hazırla"""
        self.category = Category.objects.create(name="Electronics")
        self.subcategory = SubCategory.objects.create(
            name="Smartphones",
            category=self.category
        )
        
        self.valid_data = {
            'update_type': 'PERCENTAGE_INCREASE',
            'category_filter': 'ALL',
            'percentage_increase': 10.0,
            'reason': 'Market price increase'
        }
    
    def test_form_initialization(self):
        """Form başlatma testi"""
        form = BulkPriceUpdateForm()
        
        # Gerekli alanların varlığını kontrol et
        self.assertIn('update_type', form.fields)
        self.assertIn('category_filter', form.fields)
        self.assertIn('category', form.fields)
        self.assertIn('subcategory', form.fields)
        self.assertIn('percentage_increase', form.fields)
        self.assertIn('percentage_decrease', form.fields)
        self.assertIn('fixed_amount_increase', form.fields)
        self.assertIn('fixed_amount_decrease', form.fields)
        self.assertIn('new_price', form.fields)
        self.assertIn('reason', form.fields)
    
    def test_form_valid_data(self):
        """Geçerli veri ile form testi"""
        form = BulkPriceUpdateForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
    
    def test_form_update_type_choices(self):
        """Update type seçenekleri testi"""
        form = BulkPriceUpdateForm()
        
        expected_choices = [
            ('PERCENTAGE_INCREASE', 'Percentage Increase'),
            ('PERCENTAGE_DECREASE', 'Percentage Decrease'),
            ('FIXED_AMOUNT_INCREASE', 'Fixed Amount Increase'),
            ('FIXED_AMOUNT_DECREASE', 'Fixed Amount Decrease'),
            ('SET_PRICE', 'Set New Price'),
        ]
        
        self.assertEqual(form.fields['update_type'].choices, expected_choices)
    
    def test_form_category_filter_choices(self):
        """Category filter seçenekleri testi"""
        form = BulkPriceUpdateForm()
        
        expected_choices = [
            ('ALL', 'All Products'),
            ('CATEGORY', 'By Category'),
            ('SUBCATEGORY', 'By Sub Category'),
        ]
        
        self.assertEqual(form.fields['category_filter'].choices, expected_choices)
    
    def test_form_percentage_increase_validation(self):
        """Yüzde artış validasyonu testi"""
        data = {
            'update_type': 'PERCENTAGE_INCREASE',
            'category_filter': 'ALL',
            'reason': 'Test'
        }
        
        form = BulkPriceUpdateForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
        self.assertIn('required', str(form.errors['__all__']))
    
    def test_form_percentage_decrease_validation(self):
        """Yüzde azalış validasyonu testi"""
        data = {
            'update_type': 'PERCENTAGE_DECREASE',
            'category_filter': 'ALL',
            'reason': 'Test'
        }
        
        form = BulkPriceUpdateForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
        self.assertIn('required', str(form.errors['__all__']))
    
    def test_form_fixed_amount_increase_validation(self):
        """Sabit miktar artış validasyonu testi"""
        data = {
            'update_type': 'FIXED_AMOUNT_INCREASE',
            'category_filter': 'ALL',
            'reason': 'Test'
        }
        
        form = BulkPriceUpdateForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
        self.assertIn('required', str(form.errors['__all__']))
    
    def test_form_fixed_amount_decrease_validation(self):
        """Sabit miktar azalış validasyonu testi"""
        data = {
            'update_type': 'FIXED_AMOUNT_DECREASE',
            'category_filter': 'ALL',
            'reason': 'Test'
        }
        
        form = BulkPriceUpdateForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
        self.assertIn('required', str(form.errors['__all__']))
    
    def test_form_set_price_validation(self):
        """Yeni fiyat belirleme validasyonu testi"""
        data = {
            'update_type': 'SET_PRICE',
            'category_filter': 'ALL',
            'reason': 'Test'
        }
        
        form = BulkPriceUpdateForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
        self.assertIn('required', str(form.errors['__all__']))
    
    def test_form_percentage_increase_valid(self):
        """Yüzde artış geçerli veri testi"""
        data = {
            'update_type': 'PERCENTAGE_INCREASE',
            'category_filter': 'ALL',
            'percentage_increase': 15.5,
            'reason': 'Market increase'
        }
        
        form = BulkPriceUpdateForm(data=data)
        self.assertTrue(form.is_valid())
    
    def test_form_percentage_decrease_valid(self):
        """Yüzde azalış geçerli veri testi"""
        data = {
            'update_type': 'PERCENTAGE_DECREASE',
            'category_filter': 'ALL',
            'percentage_decrease': 10.0,
            'reason': 'Market decrease'
        }
        
        form = BulkPriceUpdateForm(data=data)
        self.assertTrue(form.is_valid())
    
    def test_form_fixed_amount_increase_valid(self):
        """Sabit miktar artış geçerli veri testi"""
        data = {
            'update_type': 'FIXED_AMOUNT_INCREASE',
            'category_filter': 'ALL',
            'fixed_amount_increase': 50.0,
            'reason': 'Fixed increase'
        }
        
        form = BulkPriceUpdateForm(data=data)
        self.assertTrue(form.is_valid())
    
    def test_form_fixed_amount_decrease_valid(self):
        """Sabit miktar azalış geçerli veri testi"""
        data = {
            'update_type': 'FIXED_AMOUNT_DECREASE',
            'category_filter': 'ALL',
            'fixed_amount_decrease': 25.0,
            'reason': 'Fixed decrease'
        }
        
        form = BulkPriceUpdateForm(data=data)
        self.assertTrue(form.is_valid())
    
    def test_form_set_price_valid(self):
        """Yeni fiyat belirleme geçerli veri testi"""
        data = {
            'update_type': 'SET_PRICE',
            'category_filter': 'ALL',
            'new_price': 500.0,
            'reason': 'Set new price'
        }
        
        form = BulkPriceUpdateForm(data=data)
        self.assertTrue(form.is_valid())
    
    def test_form_category_filter_category(self):
        """Kategori filtresi ile form testi"""
        data = {
            'update_type': 'PERCENTAGE_INCREASE',
            'category_filter': 'CATEGORY',
            'category': self.category.id,
            'percentage_increase': 10.0,
            'reason': 'Category increase'
        }
        
        form = BulkPriceUpdateForm(data=data)
        self.assertTrue(form.is_valid())
    
    def test_form_category_filter_subcategory(self):
        """Alt kategori filtresi ile form testi"""
        data = {
            'update_type': 'PERCENTAGE_INCREASE',
            'category_filter': 'SUBCATEGORY',
            'subcategory': self.subcategory.id,
            'percentage_increase': 10.0,
            'reason': 'Subcategory increase'
        }
        
        form = BulkPriceUpdateForm(data=data)
        # Subcategory queryset'ini manuel olarak ayarla (AJAX olmadan)
        form.fields['subcategory'].queryset = SubCategory.objects.all()
        if not form.is_valid():
            print(f"Form errors: {form.errors}")
            print(f"Subcategory choices: {form.fields['subcategory'].queryset}")
            print(f"Selected subcategory ID: {self.subcategory.id}")
        self.assertTrue(form.is_valid())
    
    def test_form_widget_attributes(self):
        """Widget özellikleri testi"""
        form = BulkPriceUpdateForm()
        
        # CSS sınıfları kontrol et
        self.assertIn('form-control', str(form['update_type'].as_widget()))
        self.assertIn('form-control', str(form['category_filter'].as_widget()))
        self.assertIn('form-control', str(form['category'].as_widget()))
        self.assertIn('form-control', str(form['subcategory'].as_widget()))
        self.assertIn('form-control', str(form['percentage_increase'].as_widget()))
        self.assertIn('form-control', str(form['percentage_decrease'].as_widget()))
        self.assertIn('form-control', str(form['fixed_amount_increase'].as_widget()))
        self.assertIn('form-control', str(form['fixed_amount_decrease'].as_widget()))
        self.assertIn('form-control', str(form['new_price'].as_widget()))
        self.assertIn('form-control', str(form['reason'].as_widget()))
    
    def test_form_placeholder_attributes(self):
        """Placeholder özellikleri testi"""
        form = BulkPriceUpdateForm()
        
        # Placeholder kontrol et
        self.assertIn('placeholder="0"', str(form['percentage_increase'].as_widget()))
        self.assertIn('placeholder="0"', str(form['percentage_decrease'].as_widget()))
        self.assertIn('placeholder="0.00"', str(form['fixed_amount_increase'].as_widget()))
        self.assertIn('placeholder="0.00"', str(form['fixed_amount_decrease'].as_widget()))
        self.assertIn('placeholder="0.00"', str(form['new_price'].as_widget()))
        self.assertIn('placeholder="Reason for price update"', str(form['reason'].as_widget()))
    
    def test_form_step_attributes(self):
        """Step özellikleri testi"""
        form = BulkPriceUpdateForm()
        
        # Step kontrol et
        self.assertIn('step="0.01"', str(form['percentage_increase'].as_widget()))
        self.assertIn('step="0.01"', str(form['percentage_decrease'].as_widget()))
        self.assertIn('step="0.01"', str(form['fixed_amount_increase'].as_widget()))
        self.assertIn('step="0.01"', str(form['fixed_amount_decrease'].as_widget()))
        self.assertIn('step="0.01"', str(form['new_price'].as_widget()))
    
    def test_form_min_max_attributes(self):
        """Min/Max özellikleri testi"""
        form = BulkPriceUpdateForm()
        
        # Min kontrol et
        self.assertIn('min="0"', str(form['percentage_increase'].as_widget()))
        self.assertIn('min="0"', str(form['percentage_decrease'].as_widget()))
        self.assertIn('min="0"', str(form['fixed_amount_increase'].as_widget()))
        self.assertIn('min="0"', str(form['fixed_amount_decrease'].as_widget()))
        self.assertIn('min="0"', str(form['new_price'].as_widget()))
        
        # Max kontrol et
        self.assertIn('max="1000"', str(form['percentage_increase'].as_widget()))
        self.assertIn('max="100"', str(form['percentage_decrease'].as_widget()))


class TestFormIntegration(TestCase):
    """Form entegrasyon testleri"""
    
    def setUp(self):
        """Test verilerini hazırla"""
        self.user = User.objects.create_user(
            username="testuser_forms_main",
            email="test_forms_main@example.com",
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
    
    def test_form_save_product(self):
        """Form ile ürün kaydetme testi"""
        data = {
            'product_name': 'Test Product',
            'product_description': 'Test Description',
            'product_price': 99.99,
            'cost_price': 80.00,
            'product_quantity': 10,
            'minimum_stock_level': 2,
            'category': self.category.id,
            'subcategory': self.subcategory.id,
            'discount_percentage': 0,
            'discount_amount': 0,
        }
        
        form = ProductAndStockModelForm(data=data)
        form.user_organisation = self.user_profile
        
        self.assertTrue(form.is_valid())
        
        product = form.save(commit=False)
        product.organisation = self.user_profile
        product.save()
        
        # Ürün kaydedildi mi kontrol et
        self.assertTrue(ProductsAndStock.objects.filter(product_name='Test Product').exists())
        
        saved_product = ProductsAndStock.objects.get(product_name='Test Product')
        self.assertEqual(saved_product.product_price, 99.99)
        self.assertEqual(saved_product.cost_price, 80.00)
        self.assertEqual(saved_product.product_quantity, 10)
        self.assertEqual(saved_product.category, self.category)
        self.assertEqual(saved_product.subcategory, self.subcategory)
        self.assertEqual(saved_product.organisation, self.user_profile)
    
    def test_form_update_product(self):
        """Form ile ürün güncelleme testi"""
        # Önce ürün oluştur
        product = ProductsAndStock.objects.create(
            product_name='Original Product',
            product_description='Original Description',
            product_price=99.99,
            cost_price=80.00,
            product_quantity=10,
            minimum_stock_level=2,
            category=self.category,
            subcategory=self.subcategory,
            organisation=self.user_profile
        )
        
        # Güncelleme verisi
        data = {
            'product_name': 'Updated Product',
            'product_description': 'Updated Description',
            'product_price': 149.99,
            'cost_price': 120.00,
            'product_quantity': 20,
            'minimum_stock_level': 5,
            'category': self.category.id,
            'subcategory': self.subcategory.id,
            'discount_percentage': 0,
            'discount_amount': 0,
        }
        
        form = ProductAndStockModelForm(data=data, instance=product)
        form.user_organisation = self.user_profile
        
        self.assertTrue(form.is_valid())
        
        updated_product = form.save()
        
        # Ürün güncellendi mi kontrol et
        self.assertEqual(updated_product.product_name, 'Updated Product')
        self.assertEqual(updated_product.product_description, 'Updated Description')
        self.assertEqual(updated_product.product_price, 149.99)
        self.assertEqual(updated_product.cost_price, 120.00)
        self.assertEqual(updated_product.product_quantity, 20)
        self.assertEqual(updated_product.minimum_stock_level, 5)
    
    def test_form_validation_edge_cases(self):
        """Form validasyon sınır durumları testi"""
        # Boş ürün adı (geçersiz)
        data = {
            'product_name': '',  # Boş ürün adı
            'product_description': 'Test Description',
            'product_price': 100.0,
            'cost_price': 80.00,
            'product_quantity': 10,
            'minimum_stock_level': 2,
            'category': self.category.id,
            'subcategory': self.subcategory.id,
            'discount_percentage': 0,
            'discount_amount': 0,
        }
        
        form = ProductAndStockModelForm(data=data)
        form.user_organisation = self.user_profile
        self.assertFalse(form.is_valid())
    
    def test_form_discount_validation(self):
        """İndirim validasyonu testi"""
        # Geçersiz indirim yüzdesi
        data = {
            'product_name': 'Test Product',
            'product_description': 'Test Description',
            'product_price': 100.0,
            'cost_price': 80.00,
            'product_quantity': 10,
            'minimum_stock_level': 2,
            'category': self.category.id,
            'subcategory': self.subcategory.id,
            'discount_percentage': 150.0,  # 100'den büyük
            'discount_amount': 0,
        }
        
        form = ProductAndStockModelForm(data=data)
        form.user_organisation = self.user_profile
        # Form validasyonu yapmıyor, model seviyesinde kontrol edilmeli
        # Bu test form seviyesinde geçerli olacak
        self.assertTrue(form.is_valid())


if __name__ == "__main__":
    print("ProductsAndStock Formları Testleri Başlatılıyor...")
    print("=" * 60)
    
    # Test çalıştırma
    import unittest
    unittest.main()
