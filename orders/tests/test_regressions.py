"""Regressions reproduced by the live role, stock and finance checks."""
from datetime import timedelta
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.test import TestCase, TransactionTestCase
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.urls import reverse
from django.utils import timezone

from leads.models import Agent, Lead
from ProductsAndStock.models import ProductsAndStock, Category, SubCategory, StockMovement
from finance.models import OrderFinanceReport
from orders.models import orders, OrderProduct


class OrderRegressionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.owner = User.objects.create_user(username='owner-a', email='owner-a@example.com', email_verified=True)
        cls.other_owner = User.objects.create_user(username='owner-b', email='owner-b@example.com', email_verified=True)
        cls.admin = User.objects.create_superuser(username='root', email='root@example.com', password='testpass123')
        cls.org = cls.owner.userprofile
        cls.other_org = cls.other_owner.userprofile
        cls.agent_user = User.objects.create_user(username='agent-a', email='agent-a@example.com', is_agent=True, is_organisor=False, email_verified=True)
        cls.other_agent_user = User.objects.create_user(username='agent-b', email='agent-b@example.com', is_agent=True, is_organisor=False, email_verified=True)
        cls.agent = Agent.objects.create(user=cls.agent_user, organisation=cls.org)
        cls.other_agent = Agent.objects.create(user=cls.other_agent_user, organisation=cls.other_org)
        cls.lead = Lead.objects.create(first_name='Own', last_name='Lead', age=30, email='lead-a@example.com', phone_number='2025550181', organisation=cls.org, agent=cls.agent)
        cls.other_lead = Lead.objects.create(first_name='Foreign', last_name='Lead', age=30, email='lead-b@example.com', phone_number='2025550182', organisation=cls.other_org, agent=cls.other_agent)
        category = Category.objects.create(name='Regression category')
        subcategory = SubCategory.objects.create(name='Regression subcategory', category=category)
        cls.product = ProductsAndStock.objects.create(product_name='Own product', product_description='Test', product_price=100, cost_price=60, product_quantity=11, category=category, subcategory=subcategory, organisation=cls.org)
        cls.other_product = ProductsAndStock.objects.create(product_name='Foreign product', product_description='Test', product_price=25, cost_price=10, product_quantity=10, category=category, subcategory=subcategory, organisation=cls.other_org)

    def setUp(self):
        self.client.force_login(self.owner)

    def make_order(self, quantities=(2,)):
        order = orders.objects.create(order_day=timezone.now() + timedelta(days=3), order_name='Original order', order_description='Original description', organisation=self.org, lead=self.lead)
        for quantity in quantities:
            OrderProduct.objects.create(order=order, product=self.product, product_quantity=quantity)
        OrderFinanceReport.objects.create(order=order, earned_amount=order.total_order_price)
        return order

    def payload(self, quantities=(2,), order=None, **overrides):
        rows = list(order.orderproduct_set.order_by('pk')) if order else []
        data = {'order_day': (timezone.now() + timedelta(days=3)).strftime('%Y-%m-%dT%H:%M'), 'order_name': 'Updated order', 'order_description': 'Updated description', 'filter_agent': str(self.agent.pk), 'lead': str(self.lead.pk), 'orderproduct_set-TOTAL_FORMS': str(len(quantities)), 'orderproduct_set-INITIAL_FORMS': str(len(rows)), 'orderproduct_set-MIN_NUM_FORMS': '0', 'orderproduct_set-MAX_NUM_FORMS': '1000'}
        for i, quantity in enumerate(quantities):
            data[f'orderproduct_set-{i}-product'] = str(self.product.pk)
            data[f'orderproduct_set-{i}-product_quantity'] = str(quantity)
            if i < len(rows):
                data[f'orderproduct_set-{i}-id'] = str(rows[i].pk)
        data.update(overrides)
        return data

    def update(self, order, data):
        return self.client.post(reverse('orders:order-update', args=[order.pk]), data)

    def stock(self, product=None):
        return ProductsAndStock.objects.get(pk=(product or self.product).pk).product_quantity

    def test_foreign_agent_filter_never_exposes_leads(self):
        order = self.make_order()
        for user in [self.owner, self.admin]:
            self.client.force_login(user)
            for url in [reverse('orders:order-create'), reverse('orders:order-update', args=[order.pk])]:
                response = self.client.get(url, {'agent': self.other_agent.pk, 'organisation': self.org.pk})
                self.assertEqual(response.status_code, 200)
                self.assertNotIn(self.other_lead, response.context['form'].fields['lead'].queryset)

    def test_foreign_lead_is_rejected_on_create_and_update(self):
        order = self.make_order()
        data = self.payload(order=order, lead=self.other_lead.pk, filter_agent=self.other_agent.pk)
        response = self.update(order, data)
        self.assertEqual(response.status_code, 200)
        order.refresh_from_db()
        self.assertEqual(order.lead_id, self.lead.pk)
        response = self.client.post(reverse('orders:order-create'), self.payload(lead=self.other_lead.pk, filter_agent=self.other_agent.pk))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(orders.objects.count(), 1)

    def test_foreign_product_is_rejected_on_update(self):
        order = self.make_order()
        response = self.update(order, self.payload(order=order, **{'orderproduct_set-0-product': self.other_product.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(order.orderproduct_set.get().product_id, self.product.pk)
        self.assertEqual(self.stock(), 9)
        self.assertEqual(self.stock(self.other_product), 10)

    def test_model_rejects_foreign_product_without_a_form(self):
        order = self.make_order()
        with self.assertRaises(ValidationError):
            OrderProduct.objects.create(order=order, product=self.other_product, product_quantity=1)
        self.assertEqual(self.stock(self.other_product), 10)

    def test_model_rejects_foreign_lead_without_a_form(self):
        order = self.make_order()
        order.lead = self.other_lead
        with self.assertRaises(ValidationError):
            order.save()
        order.refresh_from_db()
        self.assertEqual(order.lead_id, self.lead.pk)

    def test_foreign_inline_id_cannot_be_used(self):
        order = self.make_order()
        foreign_order = orders.objects.create(order_day=timezone.now(), order_name='Foreign order', order_description='Test', organisation=self.other_org, lead=self.other_lead)
        foreign_item = OrderProduct.objects.create(order=foreign_order, product=self.other_product, product_quantity=1)
        response = self.update(order, self.payload(order=order, **{'orderproduct_set-0-id': foreign_item.pk}))
        self.assertEqual(response.status_code, 200)
        foreign_item.refresh_from_db()
        self.assertEqual(foreign_item.product_id, self.other_product.pk)
        self.assertEqual(self.stock(), 9)

    def test_duplicate_rows_over_stock_leave_no_partial_order(self):
        response = self.client.post(reverse('orders:order-create'), self.payload((6, 6)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'requested across all rows')
        self.assertFalse(orders.objects.exists())
        self.assertFalse(OrderFinanceReport.objects.exists())
        self.assertEqual(self.stock(), 11)

    def test_duplicate_rows_within_stock_are_reserved_once(self):
        response = self.client.post(reverse('orders:order-create'), self.payload((6, 5)))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.stock(), 0)
        order = orders.objects.get()
        self.assertEqual(order.total_order_price, 1100)

    def test_update_quantity_updates_stock_and_finance(self):
        order = self.make_order()
        response = self.update(order, self.payload((3,), order=order))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.stock(), 8)
        self.assertEqual(order.orderproduct_set.get().total_price, 300)
        self.assertEqual(OrderFinanceReport.objects.get(order=order).earned_amount, 300)
        finance = self.client.get(reverse('finance:financial_report'))
        self.assertEqual(finance.context['total_earned'], 300)
        self.assertEqual(finance.context['total_cost'], 180)
        self.assertEqual(finance.context['total_profit'], 120)
        self.client.post(reverse('orders:order-cancel', args=[order.pk]))
        self.assertEqual(self.stock(), 11)
        self.client.post(reverse('orders:order-cancel', args=[order.pk]))
        self.assertEqual(self.stock(), 11)

    def test_redistributing_reserved_quantities_is_allowed(self):
        order = self.make_order((6, 5))
        response = self.update(order, self.payload((9, 2), order=order))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.stock(), 0)
        self.assertEqual(list(order.orderproduct_set.order_by('pk').values_list('product_quantity', flat=True)), [9, 2])

    def test_omitting_existing_row_is_rejected(self):
        order = self.make_order((2, 3))
        data = self.payload((1,), order=order)
        data['orderproduct_set-INITIAL_FORMS'] = '1'
        response = self.update(order, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.stock(), 6)
        self.assertEqual(order.orderproduct_set.count(), 2)

    def test_invalid_update_does_not_save_order_metadata(self):
        order = self.make_order()
        response = self.update(order, self.payload((12,), order=order))
        self.assertEqual(response.status_code, 200)
        order.refresh_from_db()
        self.assertEqual(order.order_name, 'Original order')
        self.assertEqual(self.stock(), 9)
        self.assertEqual(OrderFinanceReport.objects.get(order=order).earned_amount, 200)

    def test_stock_is_revalidated_before_commit(self):
        from orders.forms import BaseOrderProductFormSet
        original_save = BaseOrderProductFormSet.save
        def reserve_then_save(formset, *args, **kwargs):
            ProductsAndStock.objects.filter(pk=self.product.pk).update(product_quantity=1)
            return original_save(formset, *args, **kwargs)
        with patch.object(BaseOrderProductFormSet, 'save', reserve_then_save):
            response = self.client.post(reverse('orders:order-create'), self.payload((2,)))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(orders.objects.exists())
        self.assertEqual(self.stock(), 11)

    def test_saved_formset_instances_still_manage_later_stock_changes(self):
        from orders.forms import OrderProductFormSet
        order = self.make_order()
        formset = OrderProductFormSet(self.payload((3,), order=order), instance=order, organisation=self.org)
        self.assertTrue(formset.is_valid(), formset.errors)
        item = formset.save()[0]
        item.product_quantity = 4
        item.save()
        self.assertEqual(self.stock(), 7)
        self.assertEqual(OrderFinanceReport.objects.get(order=order).earned_amount, 400)

    def test_cancelled_order_metadata_save_does_not_restore_twice(self):
        order = self.make_order()
        order.is_cancelled = True
        order.save()
        order.order_description = 'Changed after cancellation'
        order.save()
        order.save()
        self.assertEqual(self.stock(), 11)

    def test_deleting_active_order_restores_stock(self):
        order = self.make_order()
        response = self.client.post(reverse('orders:order-delete', args=[order.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.stock(), 11)
        self.assertFalse(OrderFinanceReport.objects.exists())

    def test_deleting_cancelled_order_does_not_restore_twice(self):
        order = self.make_order()
        order.is_cancelled = True
        order.save()
        order.delete()
        self.assertEqual(self.stock(), 11)

    def test_deleting_a_stale_line_restores_its_current_quantity(self):
        order = self.make_order()
        stale = order.orderproduct_set.get()
        current = order.orderproduct_set.get()
        current.product_quantity = 3
        current.save()
        stale.delete()
        self.assertEqual(self.stock(), 11)

    def test_product_and_organisation_cascades_still_work(self):
        self.make_order()
        self.product.delete()
        self.assertFalse(OrderProduct.objects.exists())
        self.owner.delete()
        self.assertFalse(orders.objects.exists())

    def test_owner_with_active_orders_can_be_deleted(self):
        self.make_order()
        self.owner.delete()
        self.assertFalse(OrderProduct.objects.exists())
        self.assertFalse(ProductsAndStock.objects.filter(pk=self.product.pk).exists())

    def test_switching_product_releases_old_reservation(self):
        replacement = ProductsAndStock.objects.create(
            product_name='Replacement', product_description='Test', product_price=50,
            cost_price=12,
            product_quantity=2, category=self.product.category,
            subcategory=self.product.subcategory, organisation=self.org,
        )
        order = self.make_order((11,))
        response = self.update(order, self.payload((2,), order=order, **{'orderproduct_set-0-product': replacement.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.stock(), 11)
        self.assertEqual(self.stock(replacement), 0)
        self.assertEqual(OrderFinanceReport.objects.get(order=order).earned_amount, 100)
        self.assertEqual(order.orderproduct_set.get().unit_cost, 12)

    def test_one_sided_discount_dates_are_respected(self):
        self.product.discount_percentage = 10
        self.product.discount_start_date = timezone.now() + timedelta(days=1)
        self.assertEqual(self.product.discounted_price, 100)
        self.product.discount_start_date = None
        self.product.discount_end_date = timezone.now() - timedelta(days=1)
        self.assertEqual(self.product.discounted_price, 100)
        self.product.discount_end_date = timezone.now() + timedelta(days=1)
        self.assertEqual(self.product.discounted_price, 90)

    def test_stale_product_instance_cannot_oversell(self):
        order = self.make_order((6,))
        with self.assertRaises(ValidationError):
            OrderProduct.objects.create(order=order, product=self.product, product_quantity=6)
        self.assertEqual(self.stock(), 5)
        self.assertEqual(order.orderproduct_set.count(), 1)

    def test_discount_is_recorded_and_preserved_on_later_edits(self):
        self.product.discount_percentage = 10
        self.product.discount_amount = 5
        self.product.save()
        order = self.make_order()
        item = order.orderproduct_set.get()
        self.assertEqual(item.unit_price, 85)
        self.assertEqual(item.total_price, 170)
        self.product.product_price = 200
        self.product.discount_percentage = 0
        self.product.discount_amount = 0
        self.product.save()
        response = self.update(order, self.payload((3,), order=order))
        self.assertEqual(response.status_code, 302)
        item.refresh_from_db()
        self.assertEqual(item.unit_price, 85)
        self.assertEqual(item.total_price, 255)
        self.assertEqual(OrderFinanceReport.objects.get(order=order).earned_amount, 255)
        self.assertContains(self.client.get(reverse('orders:order-detail', args=[order.pk])), '$85.00')

    def test_discount_applies_to_normal_order_creation(self):
        self.product.discount_percentage = 10
        self.product.discount_amount = 5
        self.product.save()
        response = self.client.post(reverse('orders:order-create'), self.payload())
        self.assertEqual(response.status_code, 302)
        self.assertEqual(orders.objects.get().total_order_price, 170)
        self.assertEqual(OrderFinanceReport.objects.get().earned_amount, 170)

    def test_fractional_discount_matches_the_form_preview_price(self):
        self.product.product_price = 99.99
        self.product.discount_percentage = 50
        self.product.save()
        response = self.client.get(reverse('orders:order-create'), {'agent': self.agent.pk})
        self.assertContains(response, 'data-price="50.00"')
        response = self.client.post(reverse('orders:order-create'), self.payload((2,)))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(orders.objects.get().total_order_price, 100)

    def test_catalog_changes_do_not_rewrite_reported_cost_or_profit(self):
        order = self.make_order()
        self.product.cost_price = 90
        self.product.product_price = 180
        self.product.save()
        today = timezone.localdate()
        responses = [
            self.client.get(reverse('finance:financial_report')),
            self.client.post(reverse('finance:financial_report'), {
                'start_date': today.replace(day=1).isoformat(),
                'end_date': today.isoformat(), 'date_filter': 'creation_date',
            }),
        ]
        for response in responses:
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context['total_cost'], 120)
            self.assertEqual(response.context['total_profit'], 80)
            self.assertEqual(response.context['report_rows'][0]['cost'], 120)
            self.assertEqual(response.context['report_rows'][0]['profit'], 80)
        self.assertEqual(order.orderproduct_set.get().unit_cost, 60)

    def test_quantity_edits_keep_recorded_cost(self):
        order = self.make_order()
        self.product.cost_price = 90
        self.product.save()
        response = self.update(order, self.payload((3,), order=order))
        self.assertEqual(response.status_code, 302)
        item = order.orderproduct_set.get()
        self.assertEqual(item.unit_cost, 60)
        report = self.client.get(reverse('finance:financial_report'))
        self.assertEqual(report.context['total_cost'], 180)
        self.assertEqual(report.context['total_profit'], 120)

    def test_new_lines_record_current_cost_without_changing_existing_lines(self):
        order = self.make_order()
        self.product.cost_price = 90
        self.product.save()
        response = self.update(order, self.payload((2, 1), order=order))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(list(order.orderproduct_set.order_by('pk').values_list('unit_cost', flat=True)), [60, 90])
        report = self.client.get(reverse('finance:financial_report'))
        self.assertEqual(report.context['total_cost'], 210)
        self.assertEqual(report.context['total_profit'], 90)

    def test_direct_quantity_save_cannot_overwrite_recorded_cost(self):
        order = self.make_order()
        item = order.orderproduct_set.get()
        item.product_quantity = 3
        item.unit_cost = 999
        item.save(update_fields=['product_quantity'])
        item.refresh_from_db()
        self.assertEqual(item.unit_cost, 60)
        self.assertEqual(item.total_price, 300)

    def test_unknown_historical_cost_is_not_replaced_on_quantity_edit(self):
        order = self.make_order()
        OrderProduct.objects.filter(order=order).update(unit_cost=None)
        response = self.update(order, self.payload((3,), order=order))
        self.assertEqual(response.status_code, 302)
        self.assertIsNone(order.orderproduct_set.get().unit_cost)

    def test_missing_cost_keeps_revenue_but_does_not_report_partial_profit(self):
        historical_order = self.make_order()
        known_order = self.make_order((1,))
        OrderProduct.objects.filter(order=historical_order).update(unit_cost=None)
        today = timezone.localdate()
        responses = [
            self.client.get(reverse('finance:financial_report')),
            self.client.post(reverse('finance:financial_report'), {
                'start_date': today.replace(day=1).isoformat(),
                'end_date': today.isoformat(), 'date_filter': 'creation_date',
            }),
        ]
        for response in responses:
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context['total_earned'], 300)
            self.assertIsNone(response.context['total_cost'])
            self.assertIsNone(response.context['total_profit'])
            rows = {row['report'].order_id: row for row in response.context['report_rows']}
            self.assertIsNone(rows[historical_order.pk]['cost'])
            self.assertIsNone(rows[historical_order.pk]['profit'])
            self.assertEqual(rows[known_order.pk]['cost'], 60)
            self.assertEqual(rows[known_order.pk]['profit'], 40)
            self.assertContains(response, 'Historical costs were not recorded')
            self.assertContains(response, 'Unavailable')

    def test_zero_recorded_cost_is_known_and_cancelled_unknown_cost_is_excluded(self):
        historical_order = self.make_order()
        OrderProduct.objects.filter(order=historical_order).update(unit_cost=None)
        historical_order.is_cancelled = True
        historical_order.save()
        self.product.cost_price = 0
        self.product.save()
        self.make_order((1,))
        response = self.client.get(reverse('finance:financial_report'))
        self.assertEqual(response.context['total_earned'], 100)
        self.assertEqual(response.context['total_cost'], 0)
        self.assertEqual(response.context['total_profit'], 100)
        self.assertNotContains(response, 'Historical costs were not recorded')


class OrderPriceMigrationTests(TransactionTestCase):
    def test_existing_prices_are_preserved_and_unrecorded_costs_stay_unknown(self):
        owner = get_user_model().objects.create_user(username='migration-owner', email='migration-owner@example.com')
        category = Category.objects.create(name='Migration category')
        subcategory = SubCategory.objects.create(name='Migration subcategory', category=category)
        product = ProductsAndStock.objects.create(
            product_name='Migration product', product_description='Test',
            product_price=120, cost_price=65.25, product_quantity=11, organisation=owner.userprofile,
            category=category, subcategory=subcategory,
        )
        order = orders.objects.create(order_day=timezone.now(), order_name='Historical order',
                                      order_description='Test', organisation=owner.userprofile)
        executor = MigrationExecutor(connection)
        try:
            executor.migrate([('orders', '0012_alter_orders_creation_date')])
            old_apps = executor.loader.project_state([('orders', '0012_alter_orders_creation_date')]).apps
            old_item = old_apps.get_model('orders', 'OrderProduct').objects.create(
                order_id=order.pk, product_id=product.pk, product_quantity=2, total_price=199.98,
            )
        finally:
            executor = MigrationExecutor(connection)
            executor.migrate([('orders', '0014_orderproduct_unit_cost')])
        item = OrderProduct.objects.get(pk=old_item.pk)
        self.assertAlmostEqual(item.unit_price, 99.99, places=2)
        self.assertEqual(item.total_price, 199.98)
        self.assertIsNone(item.unit_cost)
        product.refresh_from_db()
        self.assertEqual(product.product_quantity, 11)
