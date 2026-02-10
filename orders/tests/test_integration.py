# orders/tests/test_integration.py
from django.test import TestCase
from django.utils import timezone

from orders.models import orders, OrderProduct
from orders.forms import OrderProductFormSet
from leads.models import User, UserProfile, Lead
from ProductsAndStock.models import ProductsAndStock, Category, SubCategory
from finance.models import OrderFinanceReport


class OrderLifecycleIntegrationTests(TestCase):
    """Integration tests: create order with products, totals, and finance report."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='orderlife',
            email='orderlife@test.com',
            password='testpass123',
            is_organisor=True,
            email_verified=True,
            phone_number='+905551711111',
            date_of_birth='1990-01-01',
            gender='M',
        )
        self.organisation = UserProfile.objects.get(user=self.user)
        self.lead = Lead.objects.create(
            first_name='Life',
            last_name='Lead',
            email='lifelead@test.com',
            phone_number='+905551711112',
            organisation=self.organisation,
        )
        self.category = Category.objects.create(name='LifeCat', description='', icon='')
        self.subcategory = SubCategory.objects.create(
            name='LifeSub', category=self.category, description=''
        )
        self.product = ProductsAndStock.objects.create(
            product_name='LifeProduct',
            product_description='D',
            product_price=75.0,
            cost_price=40.0,
            product_quantity=50,
            minimum_stock_level=5,
            category=self.category,
            subcategory=self.subcategory,
            organisation=self.organisation,
        )

    def test_create_order_with_products_then_add_finance_report(self):
        order = orders.objects.create(
            order_day=timezone.now(),
            order_name='Integration Order',
            order_description='Desc',
            organisation=self.organisation,
            lead=self.lead,
        )
        # Create OrderProduct directly (more reliable than formset in unit tests)
        OrderProduct.objects.create(
            order=order,
            product=self.product,
            product_quantity=3,
        )
        order.refresh_from_db()
        self.assertEqual(order.items_count, 1)
        self.assertEqual(order.total_order_price, 225.0)
        report = OrderFinanceReport.objects.create(
            order=order,
            earned_amount=order.total_order_price,
        )
        self.assertEqual(report.earned_amount, 225.0)

    def test_order_total_reflects_multiple_lines(self):
        order = orders.objects.create(
            order_day=timezone.now(),
            order_name='Multi Line',
            order_description='Desc',
            organisation=self.organisation,
        )
        product2 = ProductsAndStock.objects.create(
            product_name='P2',
            product_description='D',
            product_price=20.0,
            cost_price=10.0,
            product_quantity=30,
            minimum_stock_level=0,
            category=self.category,
            subcategory=self.subcategory,
            organisation=self.organisation,
        )
        OrderProduct.objects.create(
            order=order,
            product=self.product,
            product_quantity=2,
        )
        OrderProduct.objects.create(
            order=order,
            product=product2,
            product_quantity=5,
        )
        order.refresh_from_db()
        self.assertEqual(order.items_count, 2)
        self.assertEqual(order.total_order_price, 250.0)  # 2*75 + 5*20

    def test_cancelled_order_excluded_from_finance_queryset(self):
        order = orders.objects.create(
            order_day=timezone.now(),
            order_name='Cancelled',
            order_description='Desc',
            organisation=self.organisation,
            is_cancelled=True,
        )
        OrderFinanceReport.objects.create(order=order, earned_amount=100.0)
        from finance.views import FinancialReportView
        from django.http import HttpRequest
        request = HttpRequest()
        request.user = self.user
        request.GET = {}
        request.POST = {}
        view = FinancialReportView()
        view.request = request
        start = timezone.now() - timezone.timedelta(days=30)
        end = timezone.now()
        qs = view.get_queryset(start, end, 'creation_date')
        self.assertNotIn(order, [r.order for r in qs])
