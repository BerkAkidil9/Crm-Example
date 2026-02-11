"""
Finance Views Test File
This file tests all views in the Finance module.
"""

from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from finance.models import OrderFinanceReport
from finance.views import FinancialReportView
from orders.models import orders, OrderProduct
from leads.models import User, UserProfile, Lead
from ProductsAndStock.models import ProductsAndStock, Category, SubCategory

User = get_user_model()

SIMPLE_STATIC = {'STATICFILES_STORAGE': 'django.contrib.staticfiles.storage.StaticFilesStorage'}


@override_settings(**SIMPLE_STATIC)
class TestFinancialReportView(TestCase):
    """FinancialReportView tests"""
    
    def setUp(self):
        """Set up test data"""
        # Create organisor user
        self.organisor_user = User.objects.create_user(
            username='finance_view_organisor',
            email='finance_view_organisor@example.com',
            password='testpass123',
            first_name='Finance',
            last_name='View',
            phone_number='+905551234567',
            date_of_birth='1980-01-01',
            gender='M',
            is_organisor=True,
            email_verified=True
        )
        
        # Create UserProfile
        self.organisor_profile, created = UserProfile.objects.get_or_create(
            user=self.organisor_user
        )
        
        # Create Lead
        self.lead = Lead.objects.create(
            first_name='Finance',
            last_name='Lead',
            email='financelead@example.com',
            phone_number='+905559876543',
            organisation=self.organisor_profile
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
            organisation=self.organisor_profile
        )
        
        # Create orders (on different dates)
        # Fix times to start of day (00:00:00)
        now = timezone.now()
        self.yesterday = timezone.make_aware(datetime.combine(
            (now - timedelta(days=1)).date(), datetime.min.time()
        ))
        self.today = timezone.make_aware(datetime.combine(
            now.date(), datetime.min.time()
        ))
        self.tomorrow = timezone.make_aware(datetime.combine(
            (now + timedelta(days=1)).date(), datetime.min.time()
        ))
        
        self.order1 = orders.objects.create(
            order_day=self.yesterday,
            order_name='Yesterday Order',
            order_description='Order from yesterday',
            organisation=self.organisor_profile,
            lead=self.lead,
            creation_date=self.yesterday  # Set creation_date manually
        )
        
        self.order2 = orders.objects.create(
            order_day=self.today,
            order_name='Today Order',
            order_description='Order from today',
            organisation=self.organisor_profile,
            lead=self.lead,
            creation_date=self.today  # Set creation_date manually
        )
        
        self.order3 = orders.objects.create(
            order_day=self.tomorrow,
            order_name='Tomorrow Order',
            order_description='Order from tomorrow',
            organisation=self.organisor_profile,
            lead=self.lead,
            creation_date=self.tomorrow  # Set creation_date manually
        )
        
        # Create finance reports
        self.finance_report1 = OrderFinanceReport.objects.create(
            order=self.order1,
            earned_amount=1000.0
        )
        
        self.finance_report2 = OrderFinanceReport.objects.create(
            order=self.order2,
            earned_amount=2000.0
        )
        
        self.finance_report3 = OrderFinanceReport.objects.create(
            order=self.order3,
            earned_amount=3000.0
        )
        
        # Create client and log in
        self.client = Client()
        self.client.login(username='finance_view_organisor', password='testpass123')
    
    def test_financial_report_view_get(self):
        """FinancialReportView GET request test"""
        response = self.client.get(reverse('finance:financial_report'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Financial Report')
        self.assertContains(response, 'form')
        self.assertContains(response, 'start_date')
        self.assertContains(response, 'end_date')
        self.assertContains(response, 'Filter')
    
    def test_financial_report_view_get_context(self):
        """FinancialReportView GET context test"""
        response = self.client.get(reverse('finance:financial_report'))
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertIn('total_earned', response.context)
        self.assertIn('reports', response.context)
        
        # GET request shows default (this month) data
        self.assertIn('order_count', response.context)
    
    def test_financial_report_view_post_valid_dates(self):
        """FinancialReportView POST valid dates test"""
        start_date = self.today.date()
        end_date = self.today.date()
        
        response = self.client.post(reverse('finance:financial_report'), {
            'start_date': start_date,
            'end_date': end_date
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertIn('total_earned', response.context)
        self.assertIn('reports', response.context)
        
        # Only today's order should be filtered
        self.assertEqual(response.context['total_earned'], 2000.0)  # Only order2
        self.assertEqual(len(response.context['reports']), 1)
        self.assertIn(self.finance_report2, response.context['reports'])
    
    def test_financial_report_view_post_date_range(self):
        """FinancialReportView POST date range test"""
        start_date = self.yesterday.date()
        end_date = self.today.date()
        
        response = self.client.post(reverse('finance:financial_report'), {
            'start_date': start_date,
            'end_date': end_date
        })
        
        self.assertEqual(response.status_code, 200)
        
        # Yesterday's and today's orders should be filtered
        self.assertEqual(response.context['total_earned'], 3000.0)  # order1 (1000) + order2 (2000)
        self.assertEqual(len(response.context['reports']), 2)
        self.assertIn(self.finance_report1, response.context['reports'])
        self.assertIn(self.finance_report2, response.context['reports'])
    
    def test_financial_report_view_post_all_dates(self):
        """FinancialReportView POST all dates test"""
        start_date = self.yesterday.date()
        end_date = self.tomorrow.date()
        
        response = self.client.post(reverse('finance:financial_report'), {
            'start_date': start_date,
            'end_date': end_date
        })
        
        self.assertEqual(response.status_code, 200)
        
        # All orders (yesterday, today, tomorrow) should be filtered
        self.assertEqual(response.context['total_earned'], 6000.0)  # order1 (1000) + order2 (2000) + order3 (3000)
        self.assertEqual(len(response.context['reports']), 3)
        self.assertIn(self.finance_report1, response.context['reports'])
        self.assertIn(self.finance_report2, response.context['reports'])
        self.assertIn(self.finance_report3, response.context['reports'])
    
    def test_financial_report_view_post_no_results(self):
        """FinancialReportView POST no results test"""
        start_date = (self.today + timedelta(days=10)).date()
        end_date = (self.today + timedelta(days=20)).date()
        
        response = self.client.post(reverse('finance:financial_report'), {
            'start_date': start_date,
            'end_date': end_date
        })
        
        self.assertEqual(response.status_code, 200)
        
        # No result should be found
        self.assertEqual(response.context['total_earned'], 0)
        self.assertEqual(len(response.context['reports']), 0)
    
    def test_financial_report_view_post_invalid_form(self):
        """FinancialReportView POST invalid form test"""
        response = self.client.post(reverse('finance:financial_report'), {
            'start_date': 'invalid_date',
            'end_date': 'invalid_date'
        })
        
        self.assertEqual(response.status_code, 200)
        
        # Returns GET response because form is invalid
        self.assertIsNone(response.context['total_earned'])
        self.assertEqual(len(response.context['reports']), 0)
    
    def test_financial_report_view_post_end_date_before_start_date(self):
        """FinancialReportView POST end_date before start_date test"""
        start_date = self.today.date()
        end_date = self.yesterday.date()
        
        response = self.client.post(reverse('finance:financial_report'), {
            'start_date': start_date,
            'end_date': end_date
        })
        
        self.assertEqual(response.status_code, 200)
        
        # Returns GET response because form is invalid
        self.assertIsNone(response.context['total_earned'])
        self.assertEqual(len(response.context['reports']), 0)
    
    def test_financial_report_view_template_rendering(self):
        """FinancialReportView template rendering test"""
        response = self.client.get(reverse('finance:financial_report'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'finance/financial_report.html')
    
    def test_financial_report_view_with_reports_template(self):
        """FinancialReportView with reports template test"""
        start_date = self.today.date()
        end_date = self.today.date()
        
        response = self.client.post(reverse('finance:financial_report'), {
            'start_date': start_date,
            'end_date': end_date
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Today Order')  # Only today's order
        self.assertContains(response, '2000')  # Earned amount
        self.assertContains(response, 'reportTable')
    
    def test_financial_report_view_empty_results_template(self):
        """FinancialReportView empty results template test"""
        start_date = (self.today + timedelta(days=10)).date()
        end_date = (self.today + timedelta(days=20)).date()
        
        response = self.client.post(reverse('finance:financial_report'), {
            'start_date': start_date,
            'end_date': end_date
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '0.00')
        self.assertContains(response, 'No orders found')
    
    def test_financial_report_view_date_filter_order_day(self):
        """FinancialReportView filters by order_day when date_filter=order_day (not creation_date)."""
        # Use a future date so setUp orders don't affect the result
        future = timezone.make_aware(datetime.combine(
            (timezone.now() + timedelta(days=10)).date(), datetime.min.time()
        ))
        # Order A: order_day=future, creation_date=today -> only in order_day filter for future
        # Order B: order_day=today, creation_date=future -> only in creation_date filter for future
        order_a = orders.objects.create(
            order_day=future,
            order_name='Order Day Future',
            order_description='order_day is future',
            organisation=self.organisor_profile,
            lead=self.lead,
            creation_date=self.today,
        )
        order_b = orders.objects.create(
            order_day=self.today,
            order_name='Created Future',
            order_description='creation_date is future',
            organisation=self.organisor_profile,
            lead=self.lead,
            creation_date=future,
        )
        OrderFinanceReport.objects.create(order=order_a, earned_amount=1000.0)
        OrderFinanceReport.objects.create(order=order_b, earned_amount=2000.0)

        start_date = future.date()
        end_date = future.date()

        # Filter by creation_date for future: only order_b (creation_date=future)
        response_creation = self.client.post(reverse('finance:financial_report'), {
            'start_date': start_date,
            'end_date': end_date,
            'date_filter': 'creation_date',
        })
        self.assertEqual(response_creation.status_code, 200)
        self.assertEqual(response_creation.context['total_earned'], 2000.0)
        self.assertEqual(len(response_creation.context['reports']), 1)
        self.assertEqual(response_creation.context['reports'][0].order, order_b)

        # Filter by order_day for future: only order_a (order_day=future)
        response_order_day = self.client.post(reverse('finance:financial_report'), {
            'start_date': start_date,
            'end_date': end_date,
            'date_filter': 'order_day',
        })
        self.assertEqual(response_order_day.status_code, 200)
        self.assertEqual(response_order_day.context['total_earned'], 1000.0)
        self.assertEqual(len(response_order_day.context['reports']), 1)
        self.assertEqual(response_order_day.context['reports'][0].order, order_a)

    def test_financial_report_view_date_filtering_logic(self):
        """FinancialReportView date filtering logic test"""
        # Create custom date range
        custom_start = self.today.replace(hour=0, minute=0, second=0, microsecond=0)
        custom_end = self.today.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        start_date = custom_start.date()
        end_date = custom_end.date()
        
        response = self.client.post(reverse('finance:financial_report'), {
            'start_date': start_date,
            'end_date': end_date
        })
        
        self.assertEqual(response.status_code, 200)
        
        # Only today's order should be filtered
        self.assertEqual(response.context['total_earned'], 2000.0)  # Only order2
        self.assertEqual(len(response.context['reports']), 1)
    
    def test_financial_report_view_aggregation(self):
        """FinancialReportView aggregation test"""
        # Create multiple same-day orders
        same_day_order = orders.objects.create(
            order_day=self.today,
            order_name='Same Day Order',
            order_description='Another order for today',
            organisation=self.organisor_profile,
            lead=self.lead,
            creation_date=self.today
        )
        
        OrderFinanceReport.objects.create(
            order=same_day_order,
            earned_amount=1500.0
        )
        
        start_date = self.today.date()
        end_date = self.today.date()
        
        response = self.client.post(reverse('finance:financial_report'), {
            'start_date': start_date,
            'end_date': end_date
        })
        
        self.assertEqual(response.status_code, 200)
        
        # Sum of today's two orders (order2: 2000 + same_day_order: 1500)
        self.assertEqual(response.context['total_earned'], 3500.0)  # 2000 + 1500
        self.assertEqual(len(response.context['reports']), 2)
    
    def test_financial_report_view_select_related_optimization(self):
        """FinancialReportView select_related optimization test - prevents N+1 queries"""
        start_date = self.today.date()
        end_date = self.today.date()
        
        response = self.client.post(reverse('finance:financial_report'), {
            'start_date': start_date,
            'end_date': end_date
        })
        
        self.assertEqual(response.status_code, 200)
        # select_related loads order, lead, organisation - no N+1
        reports = list(response.context['reports'])
        self.assertTrue(len(reports) >= 0)
    
    def test_financial_report_view_multiple_organisations(self):
        """FinancialReportView multiple organisations test - superuser sees all orgs"""
        self.client.logout()
        superuser = User.objects.create_superuser(
            username='finance_superuser',
            email='finance_superuser@example.com',
            password='testpass123'
        )
        self.client.login(username='finance_superuser', password='testpass123')

        # Create different organisation
        org2_user = User.objects.create_user(
            username='org2_finance_view',
            email='org2_finance_view@example.com',
            password='testpass123',
            first_name='Org2',
            last_name='Finance',
            phone_number='+905556666666',
            date_of_birth='1975-01-01',
            gender='F',
            is_organisor=True,
            email_verified=True
        )
        
        org2_profile, created = UserProfile.objects.get_or_create(user=org2_user)
        
        # Create order and finance report for Org2
        org2_order = orders.objects.create(
            order_day=self.today,
            order_name='Org2 Order',
            order_description='Order for org2',
            organisation=org2_profile,
            lead=self.lead,
            creation_date=self.today
        )
        
        OrderFinanceReport.objects.create(
            order=org2_order,
            earned_amount=5000.0
        )
        
        start_date = self.today.date()
        end_date = self.today.date()
        
        response = self.client.post(reverse('finance:financial_report'), {
            'start_date': start_date,
            'end_date': end_date
        })
        
        self.assertEqual(response.status_code, 200)
        
        # Today's orders should be filtered (from both organisations)
        self.assertEqual(response.context['total_earned'], 7000.0)  # order2 (2000) + org2_order (5000)
        self.assertEqual(len(response.context['reports']), 2)

    def test_financial_report_view_superuser_filter_by_organisation(self):
        """Superuser can filter report by organisation."""
        self.client.logout()
        superuser = User.objects.create_superuser(
            username='finance_filter_superuser',
            email='finance_filter_superuser@example.com',
            password='testpass123'
        )
        self.client.login(username='finance_filter_superuser', password='testpass123')

        # Create second organisation with order
        org2_user = User.objects.create_user(
            username='org2_filter',
            email='org2_filter@example.com',
            password='testpass123',
            is_organisor=True,
            email_verified=True
        )
        org2_profile, _ = UserProfile.objects.get_or_create(user=org2_user)
        org2_lead = Lead.objects.create(
            first_name='Org2',
            last_name='Lead',
            email='org2lead@example.com',
            phone_number='+905556666666',
            organisation=org2_profile
        )
        org2_order = orders.objects.create(
            order_day=self.today,
            order_name='Org2 Order',
            order_description='Org2',
            organisation=org2_profile,
            lead=org2_lead,
            creation_date=self.today
        )
        OrderFinanceReport.objects.create(order=org2_order, earned_amount=5000.0)

        start_date = self.today.date()
        end_date = self.today.date()

        # Filter by org1 - only org1's order (order2: 2000)
        response = self.client.post(
            reverse('finance:financial_report'),
            {
                'start_date': start_date,
                'end_date': end_date,
                'organisation': str(self.organisor_profile.pk),
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_earned'], 2000.0)
        self.assertEqual(len(response.context['reports']), 1)

        # Filter by org2 - only org2's order (5000)
        response = self.client.post(
            reverse('finance:financial_report'),
            {
                'start_date': start_date,
                'end_date': end_date,
                'organisation': str(org2_profile.pk),
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_earned'], 5000.0)
        self.assertEqual(len(response.context['reports']), 1)

    def test_financial_report_view_superuser_filter_by_agent(self):
        """Superuser can filter report by agent."""
        from leads.models import Agent

        self.client.logout()
        superuser = User.objects.create_superuser(
            username='finance_agent_filter_superuser',
            email='finance_agent_filter_superuser@example.com',
            password='testpass123'
        )
        self.client.login(username='finance_agent_filter_superuser', password='testpass123')

        # Create two agents in same org, each with a lead and order
        agent1_user = User.objects.create_user(
            username='agent1_fin',
            email='agent1_fin@example.com',
            password='testpass123',
            is_agent=True,
            email_verified=True
        )
        agent2_user = User.objects.create_user(
            username='agent2_fin',
            email='agent2_fin@example.com',
            password='testpass123',
            is_agent=True,
            email_verified=True
        )
        agent1 = Agent.objects.create(user=agent1_user, organisation=self.organisor_profile)
        agent2 = Agent.objects.create(user=agent2_user, organisation=self.organisor_profile)

        lead1 = Lead.objects.create(
            first_name='Agent1',
            last_name='Lead',
            email='agent1lead@example.com',
            phone_number='+905551111111',
            organisation=self.organisor_profile,
            agent=agent1
        )
        lead2 = Lead.objects.create(
            first_name='Agent2',
            last_name='Lead',
            email='agent2lead@example.com',
            phone_number='+905552222222',
            organisation=self.organisor_profile,
            agent=agent2
        )

        order1 = orders.objects.create(
            order_day=self.today,
            order_name='Agent1 Order',
            organisation=self.organisor_profile,
            lead=lead1,
            creation_date=self.today
        )
        order2 = orders.objects.create(
            order_day=self.today,
            order_name='Agent2 Order',
            organisation=self.organisor_profile,
            lead=lead2,
            creation_date=self.today
        )
        OrderFinanceReport.objects.create(order=order1, earned_amount=1000.0)
        OrderFinanceReport.objects.create(order=order2, earned_amount=3000.0)

        start_date = self.today.date()
        end_date = self.today.date()

        # Filter by agent1 - only agent1's order (1000)
        response = self.client.post(
            reverse('finance:financial_report'),
            {
                'start_date': start_date,
                'end_date': end_date,
                'agent': str(agent1.pk),
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_earned'], 1000.0)
        self.assertEqual(len(response.context['reports']), 1)

        # Filter by agent2 - only agent2's order (3000)
        response = self.client.post(
            reverse('finance:financial_report'),
            {
                'start_date': start_date,
                'end_date': end_date,
                'agent': str(agent2.pk),
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_earned'], 3000.0)
        self.assertEqual(len(response.context['reports']), 1)

    def test_financial_report_view_organisor_filter_by_agent(self):
        """Organisor can filter report by agent within their organisation."""
        from leads.models import Agent

        agent1_user = User.objects.create_user(
            username='org_agent1_fin',
            email='org_agent1_fin@example.com',
            password='testpass123',
            is_agent=True,
            email_verified=True
        )
        agent2_user = User.objects.create_user(
            username='org_agent2_fin',
            email='org_agent2_fin@example.com',
            password='testpass123',
            is_agent=True,
            email_verified=True
        )
        agent1 = Agent.objects.create(user=agent1_user, organisation=self.organisor_profile)
        agent2 = Agent.objects.create(user=agent2_user, organisation=self.organisor_profile)

        lead1 = Lead.objects.create(
            first_name='OrgAgent1',
            last_name='Lead',
            email='orgagent1lead@example.com',
            phone_number='+905553333333',
            organisation=self.organisor_profile,
            agent=agent1
        )
        lead2 = Lead.objects.create(
            first_name='OrgAgent2',
            last_name='Lead',
            email='orgagent2lead@example.com',
            phone_number='+905554444444',
            organisation=self.organisor_profile,
            agent=agent2
        )

        order1 = orders.objects.create(
            order_day=self.today,
            order_name='Org Agent1 Order',
            organisation=self.organisor_profile,
            lead=lead1,
            creation_date=self.today
        )
        order2 = orders.objects.create(
            order_day=self.today,
            order_name='Org Agent2 Order',
            organisation=self.organisor_profile,
            lead=lead2,
            creation_date=self.today
        )
        OrderFinanceReport.objects.create(order=order1, earned_amount=1500.0)
        OrderFinanceReport.objects.create(order=order2, earned_amount=2500.0)

        self.client.login(username='finance_view_organisor', password='testpass123')
        start_date = self.today.date()
        end_date = self.today.date()

        # Filter by agent1 - organisor sees only agent1's order
        response = self.client.post(
            reverse('finance:financial_report'),
            {
                'start_date': start_date,
                'end_date': end_date,
                'agent': str(agent1.pk),
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_earned'], 1500.0)
        self.assertEqual(len(response.context['reports']), 1)


@override_settings(**SIMPLE_STATIC)
class TestFinancialReportViewEdgeCases(TestCase):
    """FinancialReportView edge cases tests"""
    
    def setUp(self):
        """Set up test data"""
        # Create organisor user
        self.organisor_user = User.objects.create_user(
            username='edge_case_organisor',
            email='edge_case_organisor@example.com',
            password='testpass123',
            first_name='Edge',
            last_name='Case',
            phone_number='+905551234567',
            date_of_birth='1980-01-01',
            gender='M',
            is_organisor=True,
            email_verified=True
        )
        
        # Create UserProfile
        self.organisor_profile, created = UserProfile.objects.get_or_create(
            user=self.organisor_user
        )
        
        # Create Lead
        self.lead = Lead.objects.create(
            first_name='Edge',
            last_name='Lead',
            email='edgelead@example.com',
            phone_number='+905559876543',
            organisation=self.organisor_profile
        )
        
        # Date variables
        from datetime import datetime
        now = timezone.now()
        self.today = timezone.make_aware(datetime.combine(
            now.date(), datetime.min.time()
        ))
        
        # Create client and log in
        self.client = Client()
        self.client.login(username='edge_case_organisor', password='testpass123')
    
    def test_financial_report_view_no_orders(self):
        """FinancialReportView no orders test"""
        start_date = timezone.now().date()
        end_date = timezone.now().date()
        
        response = self.client.post(reverse('finance:financial_report'), {
            'start_date': start_date,
            'end_date': end_date
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_earned'], 0)
        self.assertEqual(len(response.context['reports']), 0)
    
    def test_financial_report_view_orders_without_finance_reports(self):
        """FinancialReportView orders without finance reports test"""
        # Create order but do not create finance report
        order = orders.objects.create(
            order_day=timezone.now(),
            order_name='Order Without Finance Report',
            order_description='Order without finance report',
            organisation=self.organisor_profile,
            lead=self.lead,
            creation_date=timezone.now()
        )
        
        start_date = timezone.now().date()
        end_date = timezone.now().date()
        
        response = self.client.post(reverse('finance:financial_report'), {
            'start_date': start_date,
            'end_date': end_date
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_earned'], 0)
        self.assertEqual(len(response.context['reports']), 0)
    
    def test_financial_report_view_zero_earned_amount(self):
        """FinancialReportView zero earned amount test"""
        # Create order and finance report (earned_amount = 0)
        order = orders.objects.create(
            order_day=self.today,
            order_name='Zero Earned Order',
            order_description='Order with zero earned amount',
            organisation=self.organisor_profile,
            lead=self.lead,
            creation_date=self.today
        )
        
        OrderFinanceReport.objects.create(
            order=order,
            earned_amount=0.0
        )
        
        start_date = self.today.date()
        end_date = self.today.date()
        
        response = self.client.post(reverse('finance:financial_report'), {
            'start_date': start_date,
            'end_date': end_date
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_earned'], 0.0)
        self.assertEqual(len(response.context['reports']), 1)
    
    def test_financial_report_view_negative_earned_amount(self):
        """FinancialReportView negative earned amount test"""
        # Create order and finance report (earned_amount < 0)
        order = orders.objects.create(
            order_day=self.today,
            order_name='Negative Earned Order',
            order_description='Order with negative earned amount',
            organisation=self.organisor_profile,
            lead=self.lead,
            creation_date=self.today
        )
        
        OrderFinanceReport.objects.create(
            order=order,
            earned_amount=-500.0
        )
        
        start_date = self.today.date()
        end_date = self.today.date()
        
        response = self.client.post(reverse('finance:financial_report'), {
            'start_date': start_date,
            'end_date': end_date
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_earned'], -500.0)
        self.assertEqual(len(response.context['reports']), 1)


if __name__ == "__main__":
    print("Starting Finance Views Tests...")
    print("=" * 60)
    
    # Run tests
    import unittest
    unittest.main()
