# orders/tests/test_forms.py
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from orders.models import orders, OrderProduct
from orders.forms import OrderForm, OrderModelForm, OrderProductFormSet
from leads.models import User, UserProfile, Lead
from ProductsAndStock.models import ProductsAndStock, Category, SubCategory


class OrderFormTests(TestCase):
    """Tests for OrderForm (single OrderProduct line)."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='orderform',
            email='orderform@test.com',
            password='testpass123',
            is_organisor=True,
            email_verified=True,
            phone_number='+905551411111',
            date_of_birth='1990-01-01',
            gender='M',
        )
        self.organisation = UserProfile.objects.get(user=self.user)
        self.category = Category.objects.create(name='C', description='', icon='')
        self.subcategory = SubCategory.objects.create(
            name='S', category=self.category, description=''
        )
        self.product = ProductsAndStock.objects.create(
            product_name='P1',
            product_description='D',
            product_price=10.0,
            cost_price=5.0,
            product_quantity=20,
            minimum_stock_level=0,
            category=self.category,
            subcategory=self.subcategory,
            organisation=self.organisation,
        )
        self.order = orders.objects.create(
            order_day=timezone.now(),
            order_name='Order',
            order_description='Desc',
            organisation=self.organisation,
        )

    def test_form_has_required_fields(self):
        form = OrderForm()
        self.assertIn('product', form.fields)
        self.assertIn('product_quantity', form.fields)
        self.assertFalse(form.fields['product'].required)

    def test_form_valid_with_valid_quantity(self):
        form = OrderForm(data={
            'product': self.product.pk,
            'product_quantity': 5,
        })
        self.assertTrue(form.is_valid(), form.errors)

    def test_form_invalid_quantity_exceeds_stock(self):
        form = OrderForm(data={
            'product': self.product.pk,
            'product_quantity': 25,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('product_quantity', form.errors)
        self.assertIn('Only 20 items available', str(form.errors))

    def test_form_valid_empty_product(self):
        form = OrderForm(data={
            'product': '',
            'product_quantity': 1,
        })
        self.assertTrue(form.is_valid(), form.errors)


class OrderModelFormTests(TestCase):
    """Tests for OrderModelForm (order header fields)."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='ordermodelform',
            email='ordermodelform@test.com',
            password='testpass123',
            is_organisor=True,
            email_verified=True,
            phone_number='+905551511111',
            date_of_birth='1990-01-01',
            gender='M',
        )
        self.organisation = UserProfile.objects.get(user=self.user)
        self.lead = Lead.objects.create(
            first_name='L',
            last_name='L',
            email='leadform@test.com',
            phone_number='+905551511112',
            organisation=self.organisation,
        )

    def test_form_has_expected_fields(self):
        form = OrderModelForm()
        self.assertIn('order_day', form.fields)
        self.assertIn('order_name', form.fields)
        self.assertIn('order_description', form.fields)
        self.assertIn('lead', form.fields)

    def test_form_valid_future_order_day(self):
        future = timezone.now() + timedelta(days=1)
        form = OrderModelForm(data={
            'order_day': future.strftime('%Y-%m-%dT%H:%M'),
            'order_name': 'Valid Order',
            'order_description': 'Desc',
            'lead': self.lead.pk,
        })
        self.assertTrue(form.is_valid(), form.errors)

    def test_form_invalid_past_order_day(self):
        past = timezone.now() - timedelta(days=1)
        form = OrderModelForm(data={
            'order_day': past.strftime('%Y-%m-%dT%H:%M'),
            'order_name': 'Past Order',
            'order_description': 'Desc',
            'lead': '',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('order_day', form.errors)
        self.assertIn('cannot be in the past', str(form.errors))

    def test_form_valid_without_lead(self):
        future = timezone.now() + timedelta(days=1)
        form = OrderModelForm(data={
            'order_day': future.strftime('%Y-%m-%dT%H:%M'),
            'order_name': 'No Lead',
            'order_description': 'Desc',
            'lead': '',
        })
        self.assertTrue(form.is_valid(), form.errors)


class OrderProductFormSetTests(TestCase):
    """Tests for OrderProductFormSet (inline formset)."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='formsetuser',
            email='formsetuser@test.com',
            password='testpass123',
            is_organisor=True,
            email_verified=True,
            phone_number='+905551611111',
            date_of_birth='1990-01-01',
            gender='M',
        )
        self.organisation = UserProfile.objects.get(user=self.user)
        self.category = Category.objects.create(name='C2', description='', icon='')
        self.subcategory = SubCategory.objects.create(
            name='S2', category=self.category, description=''
        )
        self.product = ProductsAndStock.objects.create(
            product_name='P2',
            product_description='D',
            product_price=100.0,
            cost_price=50.0,
            product_quantity=10,
            minimum_stock_level=0,
            category=self.category,
            subcategory=self.subcategory,
            organisation=self.organisation,
        )
        self.order = orders.objects.create(
            order_day=timezone.now(),
            order_name='FormSet Order',
            order_description='Desc',
            organisation=self.organisation,
        )

    def test_formset_creation(self):
        FormSet = OrderProductFormSet
        formset = FormSet(instance=self.order)
        self.assertEqual(formset.extra, 1)
        self.assertTrue(formset.can_delete)

    def test_formset_save_new_products(self):
        """Test formset with a single valid product line."""
        FormSet = OrderProductFormSet
        data = {
            'orderproduct_set-TOTAL_FORMS': '1',
            'orderproduct_set-INITIAL_FORMS': '0',
            'orderproduct_set-MIN_NUM_FORMS': '0',
            'orderproduct_set-MAX_NUM_FORMS': '1000',
            'orderproduct_set-0-product': str(self.product.pk),
            'orderproduct_set-0-product_quantity': '2',
            'orderproduct_set-0-DELETE': '',
        }
        formset = FormSet(data, instance=self.order)
        self.assertTrue(formset.is_valid(), formset.errors)
        formset.save()
        self.assertEqual(OrderProduct.objects.filter(order=self.order).count(), 1)
        op = OrderProduct.objects.get(order=self.order, product=self.product)
        self.assertEqual(op.product_quantity, 2)
        self.assertEqual(op.total_price, 200.0)
