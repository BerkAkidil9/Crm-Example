# finance/tests/tests.py
from datetime import datetime, timedelta

from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

from finance.models import OrderFinanceReport
from finance.forms import DateRangeForm, DATE_FILTER_CHOICES
from orders.models import orders, OrderProduct
from leads.models import UserProfile, Agent, Lead
from ProductsAndStock.models import ProductsAndStock, Category, SubCategory

User = get_user_model()

# Use simple static storage so tests don't need collectstatic
SIMPLE_STATIC = {'STATICFILES_STORAGE': 'django.contrib.staticfiles.storage.StaticFilesStorage'}


# --- Model tests ---


class OrderFinanceReportModelTests(TestCase):
    """Tests for OrderFinanceReport model."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='financeorg',
            email='financeorg@test.com',
            password='testpass123',
            is_organisor=True,
            email_verified=True,
            phone_number='+905551111111',
            date_of_birth='1990-01-01',
            gender='M',
        )
        self.organisation = UserProfile.objects.get(user=self.user)
        self.order = orders.objects.create(
            order_name="Test Order",
            order_day=timezone.now(),
            order_description="Desc",
            organisation=self.organisation,
        )

    def test_create_report(self):
        report = OrderFinanceReport.objects.create(
            order=self.order,
            earned_amount=150.50,
        )
        self.assertEqual(report.order, self.order)
        self.assertEqual(report.earned_amount, 150.50)
        self.assertIsNotNone(report.report_date)

    def test_str_representation(self):
        report = OrderFinanceReport.objects.create(
            order=self.order,
            earned_amount=100.0,
        )
        expected = f"Report for {self.order.order_name} - {report.report_date.strftime('%Y-%m-%d')}"
        self.assertEqual(str(report), expected)

    def test_one_to_one_relationship(self):
        OrderFinanceReport.objects.create(order=self.order, earned_amount=99.0)
        self.assertEqual(self.order.orderfinancereport.earned_amount, 99.0)

    def test_cascade_delete_when_order_deleted(self):
        report = OrderFinanceReport.objects.create(
            order=self.order,
            earned_amount=50.0,
        )
        pk = report.pk
        self.order.delete()
        self.assertFalse(OrderFinanceReport.objects.filter(pk=pk).exists())


# --- Form tests ---


class DateRangeFormTests(TestCase):
    """Tests for DateRangeForm."""

    def test_form_has_required_fields(self):
        form = DateRangeForm()
        self.assertIn('start_date', form.fields)
        self.assertIn('end_date', form.fields)
        self.assertIn('date_filter', form.fields)
        self.assertTrue(form.fields['start_date'].required)
        self.assertTrue(form.fields['end_date'].required)
        self.assertFalse(form.fields['date_filter'].required)

    def test_form_valid_with_valid_dates(self):
        start = timezone.localdate()
        end = start + timedelta(days=7)
        form = DateRangeForm(data={
            'start_date': start,
            'end_date': end,
            'date_filter': 'creation_date',
        })
        self.assertTrue(form.is_valid(), form.errors)

    def test_form_invalid_end_before_start(self):
        start = timezone.localdate()
        end = start - timedelta(days=1)
        form = DateRangeForm(data={
            'start_date': start,
            'end_date': end,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
        self.assertIn('End date must be after start date', str(form.errors))

    def test_form_valid_same_start_and_end(self):
        d = timezone.localdate()
        form = DateRangeForm(data={
            'start_date': d,
            'end_date': d,
            'date_filter': 'order_day',
        })
        self.assertTrue(form.is_valid(), form.errors)

    def test_form_date_filter_choices(self):
        form = DateRangeForm()
        self.assertEqual(
            list(form.fields['date_filter'].choices),
            DATE_FILTER_CHOICES,
        )

    def test_form_initial_when_no_data(self):
        form = DateRangeForm()
        self.assertIn('date_filter', form.initial)
        self.assertIn('start_date', form.initial)
        self.assertIn('end_date', form.initial)

    def test_form_invalid_missing_required(self):
        form = DateRangeForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('start_date', form.errors)
        self.assertIn('end_date', form.errors)


# --- View tests ---


@override_settings(**SIMPLE_STATIC)
class FinancialReportViewTests(TestCase):
    """Tests for FinancialReportView."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='financeorg',
            email='financeorg@test.com',
            password='testpass123',
            is_organisor=True,
            email_verified=True,
            phone_number='+905551111112',
            date_of_birth='1990-01-01',
            gender='M',
        )
        self.organisation = UserProfile.objects.get(user=self.user)
        self.client.login(username='financeorg', password='testpass123')
        self.url = reverse('finance:financial_report')
        self.order = orders.objects.create(
            order_name="Test Order",
            order_day=timezone.now(),
            order_description="Desc",
            organisation=self.organisation,
            is_cancelled=False,
        )
        self.report = OrderFinanceReport.objects.create(
            order=self.order,
            earned_amount=100.0,
        )

    def test_get_request_returns_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_get_uses_correct_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'finance/financial_report.html')

    def test_get_context_has_form(self):
        response = self.client.get(self.url)
        self.assertIn('form', response.context)

    def test_anonymous_user_redirected_to_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.url)

    def test_post_valid_date_range_returns_200(self):
        start = timezone.localdate() - timedelta(days=30)
        end = timezone.localdate()
        response = self.client.post(self.url, data={
            'start_date': start.isoformat(),
            'end_date': end.isoformat(),
            'date_filter': 'creation_date',
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('total_earned', response.context)
        self.assertIn('reports', response.context)

    def test_post_valid_shows_totals_in_context(self):
        start = timezone.localdate() - timedelta(days=30)
        end = timezone.localdate()
        response = self.client.post(self.url, data={
            'start_date': start.isoformat(),
            'end_date': end.isoformat(),
            'date_filter': 'creation_date',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_earned'], 100.0)
        self.assertEqual(response.context['order_count'], 1)
        self.assertEqual(response.context['average_per_order'], 100.0)

    def test_post_invalid_date_range_returns_200_with_errors(self):
        start = timezone.localdate()
        end = start - timedelta(days=10)
        response = self.client.post(self.url, data={
            'start_date': start.isoformat(),
            'end_date': end.isoformat(),
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertFalse(response.context['form'].is_valid())

    def test_post_empty_date_range_shows_zero_totals(self):
        # Date range where we have no orders
        start = timezone.localdate() - timedelta(days=365)
        end = start + timedelta(days=1)
        response = self.client.post(self.url, data={
            'start_date': start.isoformat(),
            'end_date': end.isoformat(),
            'date_filter': 'creation_date',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_earned'], 0)
        self.assertEqual(response.context['order_count'], 0)
        self.assertIsNone(response.context['average_per_order'])

    def test_cancelled_orders_excluded_from_report(self):
        cancelled_order = orders.objects.create(
            order_name="Cancelled Order",
            order_day=timezone.now(),
            order_description="Desc",
            organisation=self.organisation,
            is_cancelled=True,
        )
        OrderFinanceReport.objects.create(
            order=cancelled_order,
            earned_amount=999.0,
        )
        start = timezone.localdate() - timedelta(days=30)
        end = timezone.localdate()
        response = self.client.post(self.url, data={
            'start_date': start.isoformat(),
            'end_date': end.isoformat(),
            'date_filter': 'creation_date',
        })
        self.assertEqual(response.status_code, 200)
        # Only non-cancelled order should be counted
        self.assertEqual(response.context['total_earned'], 100.0)
        self.assertEqual(response.context['order_count'], 1)


@override_settings(**SIMPLE_STATIC)
class FinancialReportViewCostCalculationTests(TestCase):
    """Tests that total_cost and total_profit are calculated correctly."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='financecost',
            email='financecost@test.com',
            password='testpass123',
            is_organisor=True,
            email_verified=True,
            phone_number='+905551111113',
            date_of_birth='1990-01-01',
            gender='M',
        )
        self.organisation = UserProfile.objects.get(user=self.user)
        cat = Category.objects.create(name='TestCat', description='', icon='')
        sub = SubCategory.objects.create(name='TestSub', category=cat, description='')
        self.product = ProductsAndStock.objects.create(
            product_name='Prod',
            product_description='D',
            product_price=100.0,
            cost_price=60.0,
            product_quantity=10,
            minimum_stock_level=0,
            category=cat,
            subcategory=sub,
            organisation=self.organisation,
        )
        self.order = orders.objects.create(
            order_name="Order With Product",
            order_day=timezone.now(),
            order_description="Desc",
            organisation=self.organisation,
            is_cancelled=False,
        )
        self.order_product = OrderProduct.objects.create(
            order=self.order,
            product=self.product,
            product_quantity=2,
        )
        self.report = OrderFinanceReport.objects.create(
            order=self.order,
            earned_amount=200.0,  # 2 * 100
        )
        self.client.login(username='financecost', password='testpass123')
        self.url = reverse('finance:financial_report')

    def test_total_cost_and_profit_in_context(self):
        start = timezone.localdate() - timedelta(days=30)
        end = timezone.localdate()
        response = self.client.post(self.url, data={
            'start_date': start.isoformat(),
            'end_date': end.isoformat(),
            'date_filter': 'creation_date',
        })
        self.assertEqual(response.status_code, 200)
        # cost = 2 * 60 = 120, earned = 200, profit = 80
        self.assertEqual(response.context['total_cost'], 120.0)
        self.assertEqual(response.context['total_earned'], 200.0)
        self.assertEqual(response.context['total_profit'], 80.0)


@override_settings(**SIMPLE_STATIC)
class FinancialReportViewPermissionTests(TestCase):
    """Permission tests: organisor sees own org, agent sees own leads, admin can filter."""

    def setUp(self):
        self.client = Client()
        self.org_user = User.objects.create_user(
            username='orguser',
            email='orguser@test.com',
            password='testpass123',
            is_organisor=True,
            email_verified=True,
            phone_number='+905551111114',
            date_of_birth='1990-01-01',
            gender='M',
        )
        self.org_profile = UserProfile.objects.get(user=self.org_user)
        self.order = orders.objects.create(
            order_name="Org Order",
            order_day=timezone.now(),
            order_description="Desc",
            organisation=self.org_profile,
            is_cancelled=False,
        )
        OrderFinanceReport.objects.create(order=self.order, earned_amount=50.0)
        self.url = reverse('finance:financial_report')

    def test_organisor_sees_own_organisation_reports(self):
        self.client.login(username='orguser', password='testpass123')
        start = timezone.localdate() - timedelta(days=30)
        end = timezone.localdate()
        response = self.client.post(self.url, data={
            'start_date': start.isoformat(),
            'end_date': end.isoformat(),
            'date_filter': 'creation_date',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_earned'], 50.0)
        self.assertEqual(response.context['order_count'], 1)

    def test_superuser_sees_reports(self):
        admin = User.objects.create_superuser(
            username='adminfinance',
            email='adminfinance@test.com',
            password='adminpass123',
            phone_number='+905551111115',
            date_of_birth='1990-01-01',
            gender='M',
        )
        self.client.login(username='adminfinance', password='adminpass123')
        start = timezone.localdate() - timedelta(days=30)
        end = timezone.localdate()
        response = self.client.post(self.url, data={
            'start_date': start.isoformat(),
            'end_date': end.isoformat(),
            'date_filter': 'creation_date',
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('reports', response.context)
        self.assertIn('show_organisation_filter', response.context)
        self.assertTrue(response.context['show_organisation_filter'])
