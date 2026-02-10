"""
Tests for ProductsAndStock.models – Category, SubCategory, ProductsAndStock.
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from ProductsAndStock.models import Category, SubCategory, ProductsAndStock
from leads.models import UserProfile

User = get_user_model()


class CategoryModelTests(TestCase):
    """Tests for Category model."""

    def test_create_category(self):
        cat = Category.objects.create(name='Electronics')
        self.assertEqual(str(cat), 'Electronics')

    def test_unique_name(self):
        Category.objects.create(name='Unique')
        with self.assertRaises(Exception):
            Category.objects.create(name='Unique')


class SubCategoryModelTests(TestCase):
    """Tests for SubCategory model."""

    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name='Tech')

    def test_create_subcategory(self):
        sub = SubCategory.objects.create(name='Phones', category=self.category)
        self.assertEqual(str(sub), 'Tech - Phones')

    def test_unique_together(self):
        SubCategory.objects.create(name='Tablets', category=self.category)
        with self.assertRaises(Exception):
            SubCategory.objects.create(name='Tablets', category=self.category)


class ProductsAndStockModelTests(TestCase):
    """Tests for ProductsAndStock model – properties and validation."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='produser', email='prod@test.com', password='testpass123',
            is_organisor=True, email_verified=True,
        )
        cls.organisation = UserProfile.objects.get(user=cls.user)
        cls.category = Category.objects.create(name='ProdCat')
        cls.subcategory = SubCategory.objects.create(name='ProdSub', category=cls.category)
        cls.product = ProductsAndStock.objects.create(
            product_name='Laptop',
            product_description='A good laptop',
            product_price=1000.0,
            cost_price=600.0,
            product_quantity=50,
            minimum_stock_level=10,
            category=cls.category,
            subcategory=cls.subcategory,
            organisation=cls.organisation,
        )

    def test_str_returns_name(self):
        self.assertEqual(str(self.product), 'Laptop')

    def test_total_value(self):
        self.assertEqual(self.product.total_value, 1000.0 * 50)

    def test_is_low_stock_false(self):
        self.assertFalse(self.product.is_low_stock)

    def test_is_low_stock_true(self):
        prod = ProductsAndStock.objects.create(
            product_name='LowItem',
            product_description='Low',
            product_price=10,
            cost_price=5,
            product_quantity=3,
            minimum_stock_level=5,
            category=self.category,
            subcategory=self.subcategory,
            organisation=self.organisation,
        )
        self.assertTrue(prod.is_low_stock)

    def test_stock_status_in_stock(self):
        self.assertEqual(self.product.stock_status, 'In Stock')

    def test_stock_status_out_of_stock(self):
        prod = ProductsAndStock.objects.create(
            product_name='OOS',
            product_description='OOS',
            product_price=10,
            cost_price=5,
            product_quantity=0,
            minimum_stock_level=5,
            category=self.category,
            subcategory=self.subcategory,
            organisation=self.organisation,
        )
        self.assertEqual(prod.stock_status, 'Out of Stock')

    def test_profit_margin(self):
        self.assertAlmostEqual(self.product.profit_margin_amount, 400.0)
        self.assertAlmostEqual(
            self.product.profit_margin_percentage, (400.0 / 600.0) * 100
        )

    def test_clean_validates_subcategory_belongs_to_category(self):
        other_cat = Category.objects.create(name='OtherCat')
        other_sub = SubCategory.objects.create(name='OtherSub', category=other_cat)
        prod = ProductsAndStock(
            product_name='Bad',
            product_description='Bad',
            product_price=10,
            cost_price=5,
            product_quantity=1,
            minimum_stock_level=0,
            category=self.category,
            subcategory=other_sub,  # wrong category
            organisation=self.organisation,
        )
        with self.assertRaises(ValidationError):
            prod.clean()
