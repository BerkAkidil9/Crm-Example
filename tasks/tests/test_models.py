"""
Tests for tasks.models – Task and Notification models.
"""
from datetime import date, timedelta

from django.test import TestCase
from django.contrib.auth import get_user_model

from tasks.models import Task, Notification
from leads.models import UserProfile

User = get_user_model()


class TaskModelTests(TestCase):
    """Tests for the Task model."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='taskmod', email='taskmod@test.com', password='testpass123',
            is_organisor=True, email_verified=True,
        )
        cls.organisation = UserProfile.objects.get(user=cls.user)
        cls.task = Task.objects.create(
            title='Write tests',
            content='Write unit tests for all modules',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=7),
            status='pending',
            priority='high',
            assigned_to=cls.user,
            assigned_by=cls.user,
            organisation=cls.organisation,
        )

    def test_str_returns_title(self):
        self.assertEqual(str(self.task), 'Write tests')

    def test_default_status_is_pending(self):
        self.assertEqual(self.task.status, 'pending')

    def test_ordering_newest_first(self):
        t2 = Task.objects.create(
            title='Second task',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=1),
            assigned_to=self.user,
            organisation=self.organisation,
        )
        tasks = list(Task.objects.all())
        self.assertEqual(tasks[0].pk, t2.pk)

    def test_cascade_delete_with_user(self):
        u = User.objects.create_user(
            username='deltask', email='deltask@test.com', password='pass',
            is_organisor=True,
        )
        org = UserProfile.objects.get(user=u)
        Task.objects.create(
            title='Del', start_date=date.today(), end_date=date.today(),
            assigned_to=u, organisation=org,
        )
        u.delete()
        self.assertFalse(Task.objects.filter(title='Del').exists())

    def test_assigned_by_set_null(self):
        assigner = User.objects.create_user(
            username='assigner', email='assigner@test.com', password='pass',
        )
        task = Task.objects.create(
            title='SetNull', start_date=date.today(), end_date=date.today(),
            assigned_to=self.user, assigned_by=assigner,
            organisation=self.organisation,
        )
        assigner.delete()
        task.refresh_from_db()
        self.assertIsNone(task.assigned_by)


class NotificationModelTests(TestCase):
    """Tests for the Notification model."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='notifmod', email='notifmod@test.com', password='testpass123',
            is_organisor=True, email_verified=True,
        )
        cls.organisation = UserProfile.objects.get(user=cls.user)
        cls.task = Task.objects.create(
            title='Notif task',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=3),
            assigned_to=cls.user,
            organisation=cls.organisation,
        )

    def test_str_representation(self):
        n = Notification.objects.create(
            user=self.user, title='Deadline', message='Due soon',
            key='k1', action_url='/', action_label='Go',
        )
        self.assertIn('Deadline', str(n))
        self.assertIn('notifmod', str(n))

    def test_default_is_read_false(self):
        n = Notification.objects.create(
            user=self.user, title='Unread', message='msg', key='k2',
        )
        self.assertFalse(n.is_read)

    def test_display_url_returns_action_url(self):
        n = Notification.objects.create(
            user=self.user, title='URL', message='', key='k3',
            action_url='/custom/', action_label='Custom',
        )
        self.assertEqual(n.display_url, '/custom/')

    def test_display_url_falls_back_to_task_detail(self):
        n = Notification.objects.create(
            user=self.user, title='Fallback', message='', key='k4',
            task=self.task,
        )
        url = n.display_url
        self.assertIsNotNone(url)
        self.assertIn(str(self.task.pk), url)

    def test_display_label_falls_back_to_view_task(self):
        n = Notification.objects.create(
            user=self.user, title='LabelFB', message='', key='k5',
            task=self.task,
        )
        self.assertEqual(n.display_label, 'View Task')
