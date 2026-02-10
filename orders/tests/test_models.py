# orders/tests/test_models.py
from django.test import TestCase
from django.utils import timezone

from orders.models import orders, OrderProduct
from leads.models import User, UserProfile, Lead
from ProductsAndStock.models import ProductsAndStock, Category, SubCategory


class OrdersModelTests(TestCase):
    """Tests for orders model."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='ordermodel',
            email='ordermodel@test.com',
            password='testpass123',
            is_organisor=True,
            email_verified=True,
            phone_number='+905551211111',
            date_of_birth='1990-01-01',
            gender='M',
        )
        self.organisation = UserProfile.objects.get(user=self.user)
        self.lead = Lead.objects.create(
            first_name='Lead',
            last_name='One',
            email='leadorder@test.com',
            phone_number='+905551211112',
            organisation=self.organisation,
        )

    def test_create_order(self):
        order = orders.objects.create(
            order_day=timezone.now(),
            order_name='Test Order',
            order_description='Description',
            organisation=self.organisation,
        )
        self.assertEqual(order.order_name, 'Test Order')
        self.assertFalse(order.is_cancelled)
        self.assertIsNotNone(order.creation_date)
        self.assertIsNone(order.lead)

    def test_create_order_with_lead(self):
        order = orders.objects.create(
            order_day=timezone.now(),
            order_name='Order With Lead',
            order_description='Desc',
            organisation=self.organisation,
            lead=self.lead,
        )
        self.assertEqual(order.lead, self.lead)

    def test_str_representation(self):
        order = orders.objects.create(
            order_day=timezone.now(),
            order_name='Str Order',
            order_description='Desc',
            organisation=self.organisation,
        )
        self.assertEqual(str(order), 'Str Order')

    def test_total_order_price_empty(self):
        order = orders.objects.create(
            order_day=timezone.now(),
            order_name='Empty Order',
            order_description='Desc',
            organisation=self.organisation,
        )
        self.assertEqual(order.total_order_price, 0)
        self.assertEqual(order.items_count, 0)

    def test_cascade_delete_organisation_removes_orders(self):
        order = orders.objects.create(
            order_day=timezone.now(),
            order_name='Cascade Order',
            order_description='Desc',
            organisation=self.organisation,
        )
        pk = order.pk
        self.organisation.delete()
        self.assertFalse(orders.objects.filter(pk=pk).exists())


class OrderProductModelTests(TestCase):
    """Tests for OrderProduct model."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='opproduct',
            email='opproduct@test.com',
            password='testpass123',
            is_organisor=True,
            email_verified=True,
            phone_number='+905551311111',
            date_of_birth='1990-01-01',
            gender='M',
        )
        self.organisation = UserProfile.objects.get(user=self.user)
        self.category = Category.objects.create(name='Cat', description='', icon='')
        self.subcategory = SubCategory.objects.create(
            name='Sub', category=self.category, description=''
        )
        self.product = ProductsAndStock.objects.create(
            product_name='Product A',
            product_description='Desc',
            product_price=50.0,
            cost_price=30.0,
            product_quantity=100,
            minimum_stock_level=5,
            category=self.category,
            subcategory=self.subcategory,
            organisation=self.organisation,
        )
        self.order = orders.objects.create(
            order_day=timezone.now(),
            order_name='Order A',
            order_description='Desc',
            organisation=self.organisation,
        )

    def test_create_order_product(self):
        op = OrderProduct.objects.create(
            order=self.order,
            product=self.product,
            product_quantity=3,
        )
        self.assertEqual(op.order, self.order)
        self.assertEqual(op.product, self.product)
        self.assertEqual(op.product_quantity, 3)
        self.assertEqual(op.total_price, 150.0)  # 3 * 50

    def test_save_calculates_total_price(self):
        op = OrderProduct(
            order=self.order,
            product=self.product,
            product_quantity=2,
        )
        op.save()
        self.assertEqual(op.total_price, 100.0)

    def test_str_representation(self):
        op = OrderProduct.objects.create(
            order=self.order,
            product=self.product,
            product_quantity=1,
        )
        self.assertEqual(str(op), f'{self.order.order_name} - {self.product.product_name}')

    def test_order_total_order_price_and_items_count(self):
        OrderProduct.objects.create(
            order=self.order,
            product=self.product,
            product_quantity=2,
        )
        product2 = ProductsAndStock.objects.create(
            product_name='Product B',
            product_description='Desc',
            product_price=25.0,
            cost_price=10.0,
            product_quantity=50,
            minimum_stock_level=0,
            category=self.category,
            subcategory=self.subcategory,
            organisation=self.organisation,
        )
        OrderProduct.objects.create(
            order=self.order,
            product=product2,
            product_quantity=4,
        )
        self.order.refresh_from_db()
        self.assertEqual(self.order.items_count, 2)
        self.assertEqual(self.order.total_order_price, 200.0)  # 2*50 + 4*25
