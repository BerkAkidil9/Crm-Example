"""
Tests for orders signal handlers:
- handle_order_product_created (post_save on OrderProduct)
- handle_order_product_deleted (pre_delete on OrderProduct)
- handle_order_cancellation (post_save on orders)
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from orders.models import orders, OrderProduct
from ProductsAndStock.models import (
    ProductsAndStock, Category, SubCategory, StockMovement,
)
from leads.models import UserProfile

User = get_user_model()


class OrderSignalTestBase(TestCase):
    """Shared setup for order signal tests."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='siguser', email='siguser@test.com', password='testpass123',
            is_organisor=True, email_verified=True,
        )
        cls.organisation = UserProfile.objects.get(user=cls.user)
        cls.category = Category.objects.create(name='SigCat')
        cls.subcategory = SubCategory.objects.create(
            name='SigSub', category=cls.category,
        )

    def _make_product(self, name, qty=100, price=10.0):
        return ProductsAndStock.objects.create(
            product_name=name,
            product_description='desc',
            product_price=price,
            cost_price=price * 0.5,
            product_quantity=qty,
            minimum_stock_level=5,
            category=self.category,
            subcategory=self.subcategory,
            organisation=self.organisation,
        )

    def _make_order(self, name='TestOrder', cancelled=False):
        return orders.objects.create(
            order_day=timezone.now(),
            order_name=name,
            order_description='desc',
            organisation=self.organisation,
            is_cancelled=cancelled,
        )


class HandleOrderProductCreatedTests(OrderSignalTestBase):
    """Tests for handle_order_product_created signal."""

    def test_stock_reduced_on_order_product_create(self):
        product = self._make_product('StockReduce', qty=50)
        order = self._make_order('Ord-Reduce')
        OrderProduct.objects.create(
            order=order, product=product, product_quantity=10,
        )
        product.refresh_from_db()
        self.assertEqual(product.product_quantity, 40)

    def test_stock_movement_created_on_order_product_create(self):
        product = self._make_product('StockMov', qty=50)
        order = self._make_order('Ord-Mov')
        initial_out = StockMovement.objects.filter(
            product=product, movement_type='OUT',
        ).count()
        OrderProduct.objects.create(
            order=order, product=product, product_quantity=5,
        )
        new_out = StockMovement.objects.filter(
            product=product, movement_type='OUT',
        ).count()
        self.assertEqual(new_out, initial_out + 1)

    def test_no_stock_reduction_for_cancelled_order(self):
        product = self._make_product('NoCancelReduce', qty=50)
        order = self._make_order('Ord-Cancel', cancelled=True)
        OrderProduct.objects.create(
            order=order, product=product, product_quantity=10,
        )
        product.refresh_from_db()
        # Stock should remain unchanged for cancelled order
        self.assertEqual(product.product_quantity, 50)


class HandleOrderCancellationTests(OrderSignalTestBase):
    """Tests for handle_order_cancellation signal (post_save on orders)."""

    def test_stock_restored_on_cancellation(self):
        product = self._make_product('CancelRestore', qty=100)
        order = self._make_order('Ord-CancelRestore')
        OrderProduct.objects.create(
            order=order, product=product, product_quantity=20,
        )
        product.refresh_from_db()
        self.assertEqual(product.product_quantity, 80)

        # Cancel the order
        order.is_cancelled = True
        order.save()

        product.refresh_from_db()
        self.assertEqual(product.product_quantity, 100)

    def test_multiple_products_restored_on_cancellation(self):
        p1 = self._make_product('MultiP1', qty=50)
        p2 = self._make_product('MultiP2', qty=30)
        order = self._make_order('Ord-Multi')
        OrderProduct.objects.create(order=order, product=p1, product_quantity=10)
        OrderProduct.objects.create(order=order, product=p2, product_quantity=5)

        p1.refresh_from_db()
        p2.refresh_from_db()
        self.assertEqual(p1.product_quantity, 40)
        self.assertEqual(p2.product_quantity, 25)

        order.is_cancelled = True
        order.save()

        p1.refresh_from_db()
        p2.refresh_from_db()
        self.assertEqual(p1.product_quantity, 50)
        self.assertEqual(p2.product_quantity, 30)

    def test_stock_movement_created_on_cancellation(self):
        product = self._make_product('CancelMov', qty=100)
        order = self._make_order('Ord-CancelMov')
        OrderProduct.objects.create(
            order=order, product=product, product_quantity=15,
        )

        order.is_cancelled = True
        order.save()

        restore_movements = StockMovement.objects.filter(
            product=product,
            movement_type='IN',
            reason__icontains='Cancellation',
        )
        self.assertTrue(restore_movements.exists())
