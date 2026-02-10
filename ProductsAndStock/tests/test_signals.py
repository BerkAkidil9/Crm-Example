"""
Tests for ProductsAndStock signal handlers:
- notify_organisor_on_stock_alert (post_save on StockAlert)
"""
from django.test import TestCase
from django.contrib.auth import get_user_model

from ProductsAndStock.models import (
    ProductsAndStock, Category, SubCategory, StockAlert,
)
from tasks.models import Notification
from leads.models import UserProfile

User = get_user_model()


class NotifyOrganisorOnStockAlertTests(TestCase):
    """Tests for the notify_organisor_on_stock_alert signal."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='alertorg', email='alertorg@test.com', password='testpass123',
            is_organisor=True, email_verified=True,
        )
        cls.organisation = UserProfile.objects.get(user=cls.user)
        cls.category = Category.objects.create(name='AlertCat')
        cls.subcategory = SubCategory.objects.create(
            name='AlertSub', category=cls.category,
        )
        cls.product = ProductsAndStock.objects.create(
            product_name='AlertProduct',
            product_description='desc',
            product_price=100.0,
            cost_price=50.0,
            product_quantity=3,
            minimum_stock_level=10,
            category=cls.category,
            subcategory=cls.subcategory,
            organisation=cls.organisation,
        )

    def test_notification_created_on_new_stock_alert(self):
        """Creating a StockAlert should create a Notification for the organisor."""
        initial_count = Notification.objects.filter(user=self.user).count()
        StockAlert.objects.create(
            product=self.product,
            alert_type='LOW_STOCK',
            severity='HIGH',
            message='Stock is below minimum level',
        )
        new_count = Notification.objects.filter(user=self.user).count()
        self.assertEqual(new_count, initial_count + 1)

    def test_notification_content_includes_product_name(self):
        """The notification message should reference the product name."""
        StockAlert.objects.create(
            product=self.product,
            alert_type='OUT_OF_STOCK',
            severity='CRITICAL',
            message='Out of stock',
        )
        notification = Notification.objects.filter(user=self.user).order_by('-created_at').first()
        self.assertIsNotNone(notification)
        self.assertIn('AlertProduct', notification.message)

    def test_notification_has_action_url(self):
        """The notification should link to the product detail page."""
        StockAlert.objects.create(
            product=self.product,
            alert_type='LOW_STOCK',
            severity='MEDIUM',
            message='Low stock',
        )
        notification = Notification.objects.filter(user=self.user).order_by('-created_at').first()
        self.assertIsNotNone(notification)
        self.assertIsNotNone(notification.action_url)
        self.assertIn(str(self.product.pk), notification.action_url)

    def test_no_notification_on_alert_update(self):
        """Updating an existing StockAlert should NOT create a new notification."""
        alert = StockAlert.objects.create(
            product=self.product,
            alert_type='LOW_STOCK',
            severity='LOW',
            message='Low',
        )
        count_after_create = Notification.objects.filter(user=self.user).count()

        alert.is_resolved = True
        alert.save()

        count_after_update = Notification.objects.filter(user=self.user).count()
        self.assertEqual(count_after_create, count_after_update)
