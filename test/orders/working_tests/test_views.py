"""
Orders Views Test File
This file tests all views in the Orders module.
"""

import os
import sys
import django
from django.test import TestCase, Client
from django.urls import reverse, reverse_lazy
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.core import mail
from unittest.mock import patch, MagicMock
from django.utils import timezone

# Load Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djcrm.settings')
django.setup()

from orders.models import orders, OrderProduct
from leads.models import User, UserProfile, Lead
from ProductsAndStock.models import ProductsAndStock, Category, SubCategory
from finance.models import OrderFinanceReport

User = get_user_model()


class TestOrderListView(TestCase):
    """OrderListView testleri"""
    
    def setUp(self):
        """Set up test data"""
        # Create organisor user
        self.user = User.objects.create_user(
            username='orderlist_test_user',
            email='orderlist_test@example.com',
            password='testpass123',
            first_name='OrderList',
            last_name='Test',
            phone_number='+905551234567',
            date_of_birth='1980-01-01',
            gender='M',
            is_organisor=True,
            email_verified=True
        )
        
        # Create UserProfile
        self.user_profile, created = UserProfile.objects.get_or_create(
            user=self.user
        )
        
        # Create Lead
        self.lead = Lead.objects.create(
            first_name='Test',
            last_name='Lead',
            email='testlead@example.com',
            phone_number='+905559876543',
            organisation=self.user_profile
        )
        
        # Create orders
        self.order1 = orders.objects.create(
            order_day=timezone.now(),
            order_name='Active Order',
            order_description='Active order description',
            organisation=self.user_profile,
            lead=self.lead
        )
        
        self.order2 = orders.objects.create(
            order_day=timezone.now(),
            order_name='Cancelled Order',
            order_description='Cancelled order description',
            organisation=self.user_profile,
            lead=self.lead,
            is_cancelled=True
        )
        
        # Create test client
        self.client = Client()
    
    def test_order_list_view_requires_login(self):
        """Order list view requires login test"""
        response = self.client.get(reverse('orders:order-list'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertTrue('/login' in response.url)
    
    def test_order_list_view_authenticated_user(self):
        """Authenticated user order list view test"""
        self.client.login(username='orderlist_test_user', password='testpass123')
        response = self.client.get(reverse('orders:order-list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Active Order')
        # Template shows cancelled orders in separate section, so both active and cancelled may appear
        self.assertContains(response, 'Cancelled Order')
    
    def test_order_list_view_template(self):
        """Order list view template test"""
        self.client.login(username='orderlist_test_user', password='testpass123')
        response = self.client.get(reverse('orders:order-list'))
        
        self.assertTemplateUsed(response, 'orders/order_list.html')
    
    def test_order_list_view_context(self):
        """Order list view context test"""
        self.client.login(username='orderlist_test_user', password='testpass123')
        response = self.client.get(reverse('orders:order-list'))
        
        # Context should contain orders
        self.assertIn('object_list', response.context)
        # Template shows both active and cancelled orders
        self.assertEqual(len(response.context['object_list']), 2)  # Active and cancelled orders
        self.assertIn(self.order1, response.context['object_list'])
        self.assertIn(self.order2, response.context['object_list'])
    
    def test_order_list_view_filtered_by_organisation(self):
        """Order list view organisation filtering test"""
        # Create another user and order
        other_user = User.objects.create_user(
            username='other_user',
            email='other@example.com',
            password='testpass123',
            is_organisor=True,
            email_verified=True
        )
        other_profile, created = UserProfile.objects.get_or_create(user=other_user)
        
        other_order = orders.objects.create(
            order_day=timezone.now(),
            order_name='Other Order',
            order_description='Other order description',
            organisation=other_profile
        )
        
        self.client.login(username='orderlist_test_user', password='testpass123')
        response = self.client.get(reverse('orders:order-list'))
        
        # Should only see their own organisation's orders
        self.assertEqual(len(response.context['object_list']), 2)  # Active and cancelled
        self.assertIn(self.order1, response.context['object_list'])
        self.assertIn(self.order2, response.context['object_list'])
        self.assertNotIn(other_order, response.context['object_list'])


class TestOrderDetailView(TestCase):
    """OrderDetailView testleri"""
    
    def setUp(self):
        """Set up test data"""
        # Create organisor user
        self.user = User.objects.create_user(
            username='orderdetail_test_user',
            email='orderdetail_test@example.com',
            password='testpass123',
            first_name='OrderDetail',
            last_name='Test',
            phone_number='+905551234567',
            date_of_birth='1980-01-01',
            gender='M',
            is_organisor=True,
            email_verified=True
        )
        
        # Create UserProfile
        self.user_profile, created = UserProfile.objects.get_or_create(
            user=self.user
        )
        
        # Create Lead
        self.lead = Lead.objects.create(
            first_name='Test',
            last_name='Lead',
            email='testlead@example.com',
            phone_number='+905559876543',
            organisation=self.user_profile
        )
        
        # Create category and product
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
        
        # Create order
        self.order = orders.objects.create(
            order_day=timezone.now(),
            order_name='Detail Test Order',
            order_description='Order for detail testing',
            organisation=self.user_profile,
            lead=self.lead
        )
        
        # Create OrderProduct
        self.order_product = OrderProduct.objects.create(
            order=self.order,
            product=self.product,
            product_quantity=2,
            total_price=1999.98
        )
        
        # Create test client
        self.client = Client()
    
    def test_order_detail_view_requires_login(self):
        """Order detail view requires login test"""
        response = self.client.get(reverse('orders:order-detail', kwargs={'pk': self.order.pk}))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_order_detail_view_authenticated_user(self):
        """Authenticated user order detail view test"""
        self.client.login(username='orderdetail_test_user', password='testpass123')
        response = self.client.get(reverse('orders:order-detail', kwargs={'pk': self.order.pk}))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Detail Test Order')
        self.assertContains(response, 'iPhone 15')
    
    def test_order_detail_view_template(self):
        """Order detail view template test"""
        self.client.login(username='orderdetail_test_user', password='testpass123')
        response = self.client.get(reverse('orders:order-detail', kwargs={'pk': self.order.pk}))
        
        self.assertTemplateUsed(response, 'orders/order_detail.html')
    
    def test_order_detail_view_context(self):
        """Order detail view context test"""
        self.client.login(username='orderdetail_test_user', password='testpass123')
        response = self.client.get(reverse('orders:order-detail', kwargs={'pk': self.order.pk}))
        
        # Context should contain order and order_items
        self.assertIn('order', response.context)
        self.assertIn('order_items', response.context)
        self.assertIn('total_order_price', response.context)
        self.assertIn('leads', response.context)
        self.assertIn('products', response.context)
        
        self.assertEqual(response.context['order'], self.order)
        self.assertEqual(len(response.context['order_items']), 1)
        self.assertEqual(response.context['order_items'][0], self.order_product)
        self.assertEqual(response.context['total_order_price'], 1999.98)
    
    def test_order_detail_view_access_denied_other_organisation(self):
        """Order detail view access denied for other organisation test"""
        # Create another user
        other_user = User.objects.create_user(
            username='other_detail_user',
            email='other_detail@example.com',
            password='testpass123',
            is_organisor=True,
            email_verified=True
        )
        
        self.client.login(username='other_detail_user', password='testpass123')
        response = self.client.get(reverse('orders:order-detail', kwargs={'pk': self.order.pk}))
        
        self.assertEqual(response.status_code, 404)  # Not found (access denied)
    
    def test_order_detail_view_nonexistent_order(self):
        """Order detail view nonexistent order test"""
        self.client.login(username='orderdetail_test_user', password='testpass123')
        response = self.client.get(reverse('orders:order-detail', kwargs={'pk': 99999}))
        
        self.assertEqual(response.status_code, 404)


class TestOrderCreateView(TestCase):
    """OrderCreateView testleri"""
    
    def setUp(self):
        """Set up test data"""
        # Create organisor user
        self.user = User.objects.create_user(
            username='ordercreate_test_user',
            email='ordercreate_test@example.com',
            password='testpass123',
            first_name='OrderCreate',
            last_name='Test',
            phone_number='+905551234567',
            date_of_birth='1980-01-01',
            gender='M',
            is_organisor=True,
            email_verified=True
        )
        
        # Create UserProfile
        self.user_profile, created = UserProfile.objects.get_or_create(
            user=self.user
        )
        
        # Create Lead
        self.lead = Lead.objects.create(
            first_name='Test',
            last_name='Lead',
            email='testlead@example.com',
            phone_number='+905559876543',
            organisation=self.user_profile
        )
        
        # Create category and product
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
        
        # Create test client
        self.client = Client()
    
    def test_order_create_view_requires_login(self):
        """Order create view requires login test"""
        response = self.client.get(reverse('orders:order-create'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_order_create_view_get(self):
        """Order create view GET test"""
        self.client.login(username='ordercreate_test_user', password='testpass123')
        response = self.client.get(reverse('orders:order-create'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders/order_create.html')
        
        # Context should contain form and formset
        self.assertIn('form', response.context)
        self.assertIn('product_formset', response.context)
        self.assertIn('leads', response.context)
        self.assertIn('products', response.context)
    
    @patch('orders.views.send_mail')
    def test_order_create_view_post_success(self, mock_send_mail):
        """Order create view POST success test"""
        self.client.login(username='ordercreate_test_user', password='testpass123')
        
        # Prepare form data
        form_data = {
            'order_day': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
            'order_name': 'New Order',
            'order_description': 'New order description',
            'lead': self.lead.id,
            'orderproduct_set-TOTAL_FORMS': '1',
            'orderproduct_set-INITIAL_FORMS': '0',
            'orderproduct_set-MIN_NUM_FORMS': '0',
            'orderproduct_set-MAX_NUM_FORMS': '1000',
            'orderproduct_set-0-product': self.product.id,
            'orderproduct_set-0-product_quantity': '2',
        }
        
        response = self.client.post(reverse('orders:order-create'), form_data)
        
        # Form validation başarısız olabilir, bu durumda 200 döner
        if response.status_code == 302:
            # Should redirect on success
            self.assertRedirects(response, reverse('orders:order-list'))
        else:
            # Başarısız durumda form tekrar gösterilir
            self.assertEqual(response.status_code, 200)
            # Form hatalarını kontrol et
            self.assertContains(response, 'form')
        
        # Order should have been created
        self.assertTrue(orders.objects.filter(order_name='New Order').exists())
        order = orders.objects.get(order_name='New Order')
        
        # OrderProduct should have been created
        self.assertTrue(OrderProduct.objects.filter(order=order).exists())
        order_product = OrderProduct.objects.get(order=order)
        self.assertEqual(order_product.product, self.product)
        self.assertEqual(order_product.product_quantity, 2)
        
        # Email should have been sent
        mock_send_mail.assert_called_once()
        
        # OrderFinanceReport should have been created
        self.assertTrue(OrderFinanceReport.objects.filter(order=order).exists())
    
    def test_order_create_view_post_insufficient_stock(self):
        """Order create view POST insufficient stock test"""
        self.client.login(username='ordercreate_test_user', password='testpass123')
        
        # Reduce stock quantity
        self.product.product_quantity = 1
        self.product.save()
        
        # Prepare form data (higher quantity)
        form_data = {
            'order_day': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
            'order_name': 'Stock Test Order',
            'order_description': 'Order with insufficient stock',
            'lead': self.lead.id,
            'orderproduct_set-TOTAL_FORMS': '1',
            'orderproduct_set-INITIAL_FORMS': '0',
            'orderproduct_set-MIN_NUM_FORMS': '0',
            'orderproduct_set-MAX_NUM_FORMS': '1000',
            'orderproduct_set-0-product': self.product.id,
            'orderproduct_set-0-product_quantity': '5',
        }
        
        response = self.client.post(reverse('orders:order-create'), form_data)
        
        # Form invalid olmalı (redirect olmamalı)
        self.assertEqual(response.status_code, 200)
        
        # Order should not have been created
        self.assertFalse(orders.objects.filter(order_name='Stock Test Order').exists())
    
    def test_order_create_view_post_invalid_form(self):
        """Order create view POST invalid form test"""
        self.client.login(username='ordercreate_test_user', password='testpass123')
        
        # Invalid form data
        form_data = {
            'order_day': '',
            'order_name': '',
            'order_description': '',
            'lead': '',
        }
        
        response = self.client.post(reverse('orders:order-create'), form_data)
        
        # Form invalid olmalı
        self.assertEqual(response.status_code, 200)
        
        # Order should not have been created
        self.assertFalse(orders.objects.filter(order_name='').exists())


class TestOrderUpdateView(TestCase):
    """OrderUpdateView testleri"""
    
    def setUp(self):
        """Set up test data"""
        # Create organisor user
        self.user = User.objects.create_user(
            username='orderupdate_test_user',
            email='orderupdate_test@example.com',
            password='testpass123',
            first_name='OrderUpdate',
            last_name='Test',
            phone_number='+905551234567',
            date_of_birth='1980-01-01',
            gender='M',
            is_organisor=True,
            email_verified=True
        )
        
        # Create UserProfile
        self.user_profile, created = UserProfile.objects.get_or_create(
            user=self.user
        )
        
        # Create Lead
        self.lead = Lead.objects.create(
            first_name='Test',
            last_name='Lead',
            email='testlead@example.com',
            phone_number='+905559876543',
            organisation=self.user_profile
        )
        
        # Create order
        self.order = orders.objects.create(
            order_day=timezone.now(),
            order_name='Update Test Order',
            order_description='Order for update testing',
            organisation=self.user_profile,
            lead=self.lead
        )
        
        # Create test client
        self.client = Client()
    
    def test_order_update_view_requires_login(self):
        """Order update view requires login test"""
        response = self.client.get(reverse('orders:order-update', kwargs={'pk': self.order.pk}))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_order_update_view_get(self):
        """Order update view GET test"""
        self.client.login(username='orderupdate_test_user', password='testpass123')
        response = self.client.get(reverse('orders:order-update', kwargs={'pk': self.order.pk}))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders/order_update.html')
        
        # Context'te form olmalı
        self.assertIn('form', response.context)
        self.assertIn('leads', response.context)
        self.assertIn('products', response.context)
    
    def test_order_update_view_post_success(self):
        """Order update view POST success test"""
        self.client.login(username='orderupdate_test_user', password='testpass123')
        
        # Prepare form data
        form_data = {
            'order_day': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
            'order_name': 'Updated Order Name',
            'order_description': 'Updated order description',
            'lead': self.lead.id,
        }
        
        response = self.client.post(
            reverse('orders:order-update', kwargs={'pk': self.order.pk}),
            form_data
        )
        
        # Should redirect
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('orders:order-list'))
        
        # Order should have been updated
        self.order.refresh_from_db()
        self.assertEqual(self.order.order_name, 'Updated Order Name')
        self.assertEqual(self.order.order_description, 'Updated order description')
    
    def test_order_update_view_access_denied_other_organisation(self):
        """Order update view access denied for other organisation test"""
        # Create another user
        other_user = User.objects.create_user(
            username='other_update_user',
            email='other_update@example.com',
            password='testpass123',
            is_organisor=True,
            email_verified=True
        )
        
        self.client.login(username='other_update_user', password='testpass123')
        response = self.client.get(reverse('orders:order-update', kwargs={'pk': self.order.pk}))
        
        self.assertEqual(response.status_code, 404)  # Not found (access denied)


class TestOrderCancelView(TestCase):
    """OrderCancelView testleri"""
    
    def setUp(self):
        """Set up test data"""
        # Create organisor user
        self.user = User.objects.create_user(
            username='ordercancel_test_user',
            email='ordercancel_test@example.com',
            password='testpass123',
            first_name='OrderCancel',
            last_name='Test',
            phone_number='+905551234567',
            date_of_birth='1980-01-01',
            gender='M',
            is_organisor=True,
            email_verified=True
        )
        
        # Create UserProfile
        self.user_profile, created = UserProfile.objects.get_or_create(
            user=self.user
        )
        
        # Create Lead
        self.lead = Lead.objects.create(
            first_name='Test',
            last_name='Lead',
            email='testlead@example.com',
            phone_number='+905559876543',
            organisation=self.user_profile
        )
        
        # Create category and product
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
        
        # Create order
        self.order = orders.objects.create(
            order_day=timezone.now(),
            order_name='Cancel Test Order',
            order_description='Order for cancel testing',
            organisation=self.user_profile,
            lead=self.lead
        )
        
        # Create OrderProduct
        self.order_product = OrderProduct.objects.create(
            order=self.order,
            product=self.product,
            product_quantity=5,
            total_price=4999.95
        )
        
        # Create test client
        self.client = Client()
    
    def test_order_cancel_view_post_success(self):
        """Order cancel view POST success test"""
        initial_stock = self.product.product_quantity
        
        response = self.client.post(reverse('orders:order-cancel', kwargs={'pk': self.order.pk}))
        
        # Should redirect
        self.assertEqual(response.status_code, 302)
        # Check redirect URL (content check instead of exact match)
        self.assertTrue(response.url.endswith('/orders/'))
        
        # Order should be cancelled
        self.order.refresh_from_db()
        self.assertTrue(self.order.is_cancelled)
        
        # Stock should have been restored
        self.product.refresh_from_db()
        self.assertEqual(self.product.product_quantity, initial_stock + 5)
    
    def test_order_cancel_view_post_already_cancelled(self):
        """Order cancel view POST already cancelled order test"""
        # Cancel the order
        self.order.is_cancelled = True
        self.order.save()
        
        response = self.client.post(reverse('orders:order-cancel', kwargs={'pk': self.order.pk}))
        
        # Should redirect
        self.assertEqual(response.status_code, 302)
        # Check redirect URL (content check instead of exact match)
        self.assertTrue(response.url.endswith('/orders/'))
        
        # Check session for message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('already been canceled' in str(message) for message in messages))
    
    def test_order_cancel_view_nonexistent_order(self):
        """Order cancel view nonexistent order test"""
        response = self.client.post(reverse('orders:order-cancel', kwargs={'pk': 99999}))
        
        self.assertEqual(response.status_code, 404)


class TestOrderDeleteView(TestCase):
    """OrderDeleteView testleri"""
    
    def setUp(self):
        """Set up test data"""
        # Create organisor user
        self.user = User.objects.create_user(
            username='orderdelete_test_user',
            email='orderdelete_test@example.com',
            password='testpass123',
            first_name='OrderDelete',
            last_name='Test',
            phone_number='+905551234567',
            date_of_birth='1980-01-01',
            gender='M',
            is_organisor=True,
            email_verified=True
        )
        
        # Create UserProfile
        self.user_profile, created = UserProfile.objects.get_or_create(
            user=self.user
        )
        
        # Create Lead
        self.lead = Lead.objects.create(
            first_name='Test',
            last_name='Lead',
            email='testlead@example.com',
            phone_number='+905559876543',
            organisation=self.user_profile
        )
        
        # Create order
        self.order = orders.objects.create(
            order_day=timezone.now(),
            order_name='Delete Test Order',
            order_description='Order for delete testing',
            organisation=self.user_profile,
            lead=self.lead
        )
        
        # Create test client
        self.client = Client()
    
    def test_order_delete_view_requires_login(self):
        """Order delete view requires login test"""
        response = self.client.get(reverse('orders:order-delete', kwargs={'pk': self.order.pk}))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_order_delete_view_get(self):
        """Order delete view GET test"""
        self.client.login(username='orderdelete_test_user', password='testpass123')
        response = self.client.get(reverse('orders:order-delete', kwargs={'pk': self.order.pk}))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders/order_delete.html')
        
        # Context should contain order
        self.assertIn('object', response.context)
        self.assertEqual(response.context['object'], self.order)
    
    def test_order_delete_view_post_success(self):
        """Order delete view POST success test"""
        self.client.login(username='orderdelete_test_user', password='testpass123')
        
        order_id = self.order.id
        response = self.client.post(reverse('orders:order-delete', kwargs={'pk': self.order.pk}))
        
        # Should redirect
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('orders:order-list'))
        
        # Order should have been deleted
        self.assertFalse(orders.objects.filter(id=order_id).exists())
    
    def test_order_delete_view_access_denied_other_organisation(self):
        """Order delete view access denied for other organisation test"""
        # Create another user
        other_user = User.objects.create_user(
            username='other_delete_user',
            email='other_delete@example.com',
            password='testpass123',
            is_organisor=True,
            email_verified=True
        )
        
        self.client.login(username='other_delete_user', password='testpass123')
        response = self.client.get(reverse('orders:order-delete', kwargs={'pk': self.order.pk}))
        
        self.assertEqual(response.status_code, 404)  # Not found (access denied)
    
    def test_order_delete_view_cancel_order_action(self):
        """Order delete view cancel order action testi"""
        self.client.login(username='orderdelete_test_user', password='testpass123')
        
        # POST with cancel order action
        response = self.client.post(
            reverse('orders:order-delete', kwargs={'pk': self.order.pk}),
            {'cancel_order': 'Cancel Order'}
        )
        
        # Should redirect
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('orders:order-list'))
        
        # Order should be cancelled (not deleted)
        self.order.refresh_from_db()
        self.assertTrue(self.order.is_cancelled)
        self.assertTrue(orders.objects.filter(id=self.order.id).exists())


if __name__ == "__main__":
    print("Starting Orders Views Tests...")
    print("=" * 60)
    
    # Run tests
    import unittest
    unittest.main()
