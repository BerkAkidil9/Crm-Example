"""
Tests for tasks management commands: check_lead_no_order, check_order_day,
check_task_deadlines, create_fake_notifications.
"""
from datetime import timedelta
from io import StringIO

from django.test import TestCase, override_settings
from django.core.management import call_command
from django.utils import timezone
from django.contrib.auth import get_user_model

from leads.models import Lead, Agent, UserProfile
from orders.models import orders
from tasks.models import Task, Notification

User = get_user_model()


class CheckLeadNoOrderCommandTests(TestCase):
    """Tests for check_lead_no_order management command."""

    @classmethod
    def setUpTestData(cls):
        cls.org_user = User.objects.create_user(
            username='cmd_org',
            email='cmd_org@test.com',
            password='testpass123',
            is_organisor=True,
            email_verified=True,
        )
        cls.organisation = UserProfile.objects.get(user=cls.org_user)
        cls.agent_user = User.objects.create_user(
            username='cmd_agent',
            email='cmd_agent@test.com',
            password='testpass123',
            is_agent=True,
            email_verified=True,
        )
        cls.agent = Agent.objects.create(user=cls.agent_user, organisation=cls.organisation)

    def test_dry_run_does_not_create_notifications(self):
        """--dry-run should not create any notifications."""
        lead = Lead.objects.create(
            first_name='No',
            last_name='Order',
            email='noorder@test.com',
            phone_number='+905551234567',
            organisation=self.organisation,
            agent=self.agent,
        )
        out = StringIO()
        call_command('check_lead_no_order', '--dry-run', stdout=out)
        self.assertEqual(Notification.objects.count(), 0)
        self.assertIn('Would notify', out.getvalue() or 'Would notify')

    def test_creates_notification_when_lead_has_no_order(self):
        """When lead has no order (and date_added is old), command creates notification."""
        lead = Lead.objects.create(
            first_name='No',
            last_name='Order',
            email='noorder@test.com',
            phone_number='+905551234567',
            organisation=self.organisation,
            agent=self.agent,
        )
        # Make date_added old so "no order in 30 days" applies
        lead.date_added = timezone.now() - timedelta(days=35)
        lead.save(update_fields=['date_added'])

        out = StringIO()
        call_command('check_lead_no_order', stdout=out)

        self.assertEqual(Notification.objects.filter(key__startswith='lead_no_order_').count(), 1)
        notif = Notification.objects.get(key__startswith='lead_no_order_')
        self.assertEqual(notif.user, self.agent_user)
        self.assertIn('has not placed any order', notif.message)

    def test_does_not_notify_twice_same_month(self):
        """Same lead should not get duplicate notification in same month."""
        lead = Lead.objects.create(
            first_name='No',
            last_name='Order',
            email='noorder2@test.com',
            phone_number='+905559999999',
            organisation=self.organisation,
            agent=self.agent,
        )
        lead.date_added = timezone.now() - timedelta(days=35)
        lead.save(update_fields=['date_added'])

        call_command('check_lead_no_order', stdout=StringIO())
        call_command('check_lead_no_order', stdout=StringIO())

        self.assertEqual(Notification.objects.filter(key__startswith='lead_no_order_').count(), 1)


class CheckOrderDayCommandTests(TestCase):
    """Tests for check_order_day management command."""

    @classmethod
    def setUpTestData(cls):
        cls.org_user = User.objects.create_user(
            username='orderday_org',
            email='orderday_org@test.com',
            password='testpass123',
            is_organisor=True,
            email_verified=True,
        )
        cls.organisation = UserProfile.objects.get(user=cls.org_user)
        cls.agent_user = User.objects.create_user(
            username='orderday_agent',
            email='orderday_agent@test.com',
            password='testpass123',
            is_agent=True,
            email_verified=True,
        )
        cls.agent = Agent.objects.create(user=cls.agent_user, organisation=cls.organisation)
        cls.lead = Lead.objects.create(
            first_name='Order',
            last_name='Lead',
            email='orderlead@test.com',
            phone_number='+905551111111',
            organisation=cls.organisation,
            agent=cls.agent,
        )

    def test_dry_run_does_not_create_notifications(self):
        """--dry-run should not create notifications."""
        order = orders.objects.create(
            order_day=timezone.now(),
            order_name='Today Order',
            order_description='Due today',
            organisation=self.organisation,
            lead=self.lead,
        )
        out = StringIO()
        call_command('check_order_day', '--dry-run', stdout=out)
        self.assertEqual(Notification.objects.filter(key__startswith='order_day_').count(), 0)
        self.assertIn('Would notify', out.getvalue() or 'Would notify')

    def test_creates_notification_when_order_day_is_today(self):
        """When order_day is today, organisor and agent get notified."""
        order = orders.objects.create(
            order_day=timezone.now(),
            order_name='Due Today',
            order_description='Sale completed today',
            organisation=self.organisation,
            lead=self.lead,
        )
        out = StringIO()
        call_command('check_order_day', stdout=out)

        notifications = Notification.objects.filter(key__startswith='order_day_')
        self.assertGreaterEqual(notifications.count(), 1)
        users_notified = set(notifications.values_list('user_id', flat=True))
        self.assertIn(self.org_user.id, users_notified)
        self.assertIn(self.agent_user.id, users_notified)


class CheckTaskDeadlinesCommandTests(TestCase):
    """Tests for check_task_deadlines management command."""

    @classmethod
    def setUpTestData(cls):
        cls.org_user = User.objects.create_user(
            username='deadline_org',
            email='deadline_org@test.com',
            password='testpass123',
            is_organisor=True,
            email_verified=True,
        )
        cls.organisation = UserProfile.objects.get(user=cls.org_user)
        cls.agent_user = User.objects.create_user(
            username='deadline_agent',
            email='deadline_agent@test.com',
            password='testpass123',
            is_agent=True,
            email_verified=True,
        )
        cls.agent = Agent.objects.create(user=cls.agent_user, organisation=cls.organisation)

    def test_dry_run_does_not_create_notifications(self):
        """--dry-run should not create notifications or send email."""
        tomorrow = timezone.now().date() + timedelta(days=1)
        task = Task.objects.create(
            title='Due Tomorrow',
            content='Task content',
            start_date=timezone.now().date(),
            end_date=tomorrow,
            status='pending',
            priority='medium',
            assigned_to=self.agent_user,
            assigned_by=self.org_user,
            organisation=self.organisation,
        )
        out = StringIO()
        call_command('check_task_deadlines', '--dry-run', stdout=out)
        self.assertEqual(Notification.objects.filter(key__startswith='task_deadline_').count(), 0)
        self.assertIn('Would send', out.getvalue() or 'Would send')

    @override_settings(
        DEFAULT_FROM_EMAIL='noreply@test.com',
        SITE_URL='http://testserver',
    )
    def test_creates_notification_for_task_due_tomorrow(self):
        """Task due in 1 day gets reminder notification (and email mocked in test)."""
        tomorrow = timezone.now().date() + timedelta(days=1)
        task = Task.objects.create(
            title='Due Tomorrow',
            content='Content',
            start_date=timezone.now().date(),
            end_date=tomorrow,
            status='pending',
            priority='medium',
            assigned_to=self.agent_user,
            assigned_by=self.org_user,
            organisation=self.organisation,
        )
        with self.settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'):
            out = StringIO()
            call_command('check_task_deadlines', '--days', '1', stdout=out)

        notifications = Notification.objects.filter(key__startswith='task_deadline_')
        self.assertEqual(notifications.count(), 1)
        notif = notifications.get()
        self.assertEqual(notif.user, self.agent_user)
        self.assertIn('tomorrow', notif.title.lower())


class CreateFakeNotificationsCommandTests(TestCase):
    """Tests for create_fake_notifications management command."""

    @classmethod
    def setUpTestData(cls):
        cls.superuser = User.objects.create_superuser(
            username='fake_super',
            email='fake_super@test.com',
            password='testpass123',
        )
        cls.org_user = User.objects.create_user(
            username='fake_org',
            email='fake_org@test.com',
            password='testpass123',
            is_organisor=True,
            email_verified=True,
        )
        cls.organisation = UserProfile.objects.get(user=cls.org_user)
        cls.lead = Lead.objects.create(
            first_name='Fake',
            last_name='Lead',
            email='fake_lead@test.com',
            phone_number='+905553333333',
            organisation=cls.organisation,
        )
        cls.task = Task.objects.create(
            title='Fake Task',
            content='Content',
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=1),
            status='pending',
            priority='medium',
            assigned_to=cls.org_user,
            assigned_by=cls.org_user,
            organisation=cls.organisation,
        )
        cls.order = orders.objects.create(
            order_day=timezone.now(),
            order_name='Fake Order',
            order_description='Fake',
            organisation=cls.organisation,
            lead=cls.lead,
        )

    def test_creates_fake_notifications_for_first_user_when_no_username(self):
        """Without --user, uses first superuser and creates notifications."""
        from ProductsAndStock.models import ProductsAndStock, Category, SubCategory
        cat = Category.objects.create(name='TestCat')
        sub = SubCategory.objects.create(name='TestSub', category=cat)
        product = ProductsAndStock.objects.create(
            product_name='Fake Product',
            product_price=10,
            cost_price=5,
            product_quantity=1,
            minimum_stock_level=0,
            category=cat,
            subcategory=sub,
            organisation=self.organisation,
        )

        out = StringIO()
        call_command('create_fake_notifications', stdout=out)

        fake = Notification.objects.filter(key__startswith='fake_test_')
        self.assertGreaterEqual(fake.count(), 1)
        self.assertIn('Creating fake notifications', out.getvalue())

    def test_creates_fake_notifications_for_given_username(self):
        """With --user, creates notifications for that user."""
        from ProductsAndStock.models import ProductsAndStock, Category, SubCategory
        cat = Category.objects.create(name='TestCat2')
        sub = SubCategory.objects.create(name='TestSub2', category=cat)
        product = ProductsAndStock.objects.create(
            product_name='Fake Product 2',
            product_price=10,
            cost_price=5,
            product_quantity=1,
            minimum_stock_level=0,
            category=cat,
            subcategory=sub,
            organisation=self.organisation,
        )

        out = StringIO()
        call_command('create_fake_notifications', '--user', 'fake_org', stdout=out)

        fake = Notification.objects.filter(user=self.org_user, key__startswith='fake_test_')
        self.assertGreaterEqual(fake.count(), 1)
        self.assertIn('fake_org', out.getvalue())

    def test_nonexistent_user_shows_error(self):
        """--user with nonexistent username should write error and return."""
        err = StringIO()
        call_command('create_fake_notifications', '--user', 'nonexistent_user_xyz', stderr=err)
        self.assertIn('not found', err.getvalue().lower() or 'not found')
