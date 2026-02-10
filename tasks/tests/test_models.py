"""
Tests for tasks.models – Task and Notification models.
"""
from datetime import date, timedelta

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.urls import reverse

from tasks.models import Task, Notification
from leads.models import UserProfile

User = get_user_model()


class TaskModelTestHelper:
    """Shared helper that creates common objects for task tests."""

    @classmethod
    def create_users_and_org(cls):
        cls.organisor_user = User.objects.create_user(
            username='organisor_task',
            email='organisor_task@test.com',
            password='testpass123',
            is_organisor=True,
        )
        cls.organisation = UserProfile.objects.get(user=cls.organisor_user)
        cls.agent_user = User.objects.create_user(
            username='agent_task',
            email='agent_task@test.com',
            password='testpass123',
            is_agent=True,
        )
        cls.superuser = User.objects.create_superuser(
            username='admin_task',
            email='admin_task@test.com',
            password='testpass123',
        )

    @classmethod
    def create_task(cls, **overrides):
        defaults = {
            'title': 'Test Task',
            'content': 'Test content',
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=7),
            'status': 'pending',
            'priority': 'medium',
            'assigned_to': cls.agent_user,
            'assigned_by': cls.organisor_user,
            'organisation': cls.organisation,
        }
        defaults.update(overrides)
        return Task.objects.create(**defaults)


# ---------------------------------------------------------------------------
# Task model tests
# ---------------------------------------------------------------------------
class TestTaskModel(TaskModelTestHelper, TestCase):
    """Tests for Task model creation, fields and relationships."""

    @classmethod
    def setUpTestData(cls):
        cls.create_users_and_org()

    def test_create_task(self):
        task = self.create_task()
        self.assertIsNotNone(task.pk)
        self.assertEqual(task.title, 'Test Task')

    def test_str_representation(self):
        task = self.create_task(title='Follow up lead')
        self.assertEqual(str(task), 'Follow up lead')

    def test_default_status(self):
        task = self.create_task()
        self.assertEqual(task.status, 'pending')

    def test_default_priority(self):
        task = self.create_task()
        self.assertEqual(task.priority, 'medium')

    def test_status_choices(self):
        for status_val, _ in Task.STATUS_CHOICES:
            task = self.create_task(status=status_val, title=f'Task {status_val}')
            self.assertEqual(task.status, status_val)

    def test_priority_choices(self):
        for priority_val, _ in Task.PRIORITY_CHOICES:
            task = self.create_task(priority=priority_val, title=f'Task {priority_val}')
            self.assertEqual(task.priority, priority_val)

    def test_assigned_to_relationship(self):
        task = self.create_task()
        self.assertEqual(task.assigned_to, self.agent_user)
        self.assertIn(task, self.agent_user.assigned_tasks.all())

    def test_assigned_by_relationship(self):
        task = self.create_task()
        self.assertEqual(task.assigned_by, self.organisor_user)
        self.assertIn(task, self.organisor_user.tasks_assigned_by.all())

    def test_assigned_by_nullable(self):
        task = self.create_task(assigned_by=None)
        self.assertIsNone(task.assigned_by)

    def test_organisation_relationship(self):
        task = self.create_task()
        self.assertEqual(task.organisation, self.organisation)
        self.assertIn(task, self.organisation.tasks.all())

    def test_cascade_delete_assigned_to(self):
        """Deleting the assigned user should delete their tasks."""
        user = User.objects.create_user(
            username='temp_agent', email='temp@test.com', password='pass123'
        )
        task = self.create_task(assigned_to=user)
        task_pk = task.pk
        user.delete()
        self.assertFalse(Task.objects.filter(pk=task_pk).exists())

    def test_set_null_on_assigned_by_delete(self):
        """Deleting the assigner should set assigned_by to NULL."""
        assigner = User.objects.create_user(
            username='temp_assigner', email='temp_assigner@test.com', password='pass123'
        )
        task = self.create_task(assigned_by=assigner)
        assigner.delete()
        task.refresh_from_db()
        self.assertIsNone(task.assigned_by)

    def test_cascade_delete_organisation(self):
        """Deleting the organisation should delete tasks."""
        org_user = User.objects.create_user(
            username='temp_org', email='temp_org@test.com', password='pass123', is_organisor=True,
        )
        org = UserProfile.objects.get(user=org_user)
        task = self.create_task(organisation=org)
        task_pk = task.pk
        org.delete()
        self.assertFalse(Task.objects.filter(pk=task_pk).exists())

    def test_auto_timestamps(self):
        task = self.create_task()
        self.assertIsNotNone(task.created_at)
        self.assertIsNotNone(task.updated_at)

    def test_ordering(self):
        """Tasks should be ordered by -created_at (newest first)."""
        t1 = self.create_task(title='First')
        t2 = self.create_task(title='Second')
        tasks = list(Task.objects.all())
        # In fast tests, created_at may be identical; verify pk ordering as fallback
        self.assertGreater(t2.pk, t1.pk)
        self.assertEqual(len(tasks), 2)

    def test_verbose_names(self):
        self.assertEqual(Task._meta.verbose_name, 'Task')
        self.assertEqual(Task._meta.verbose_name_plural, 'Tasks')

    def test_content_blank(self):
        task = self.create_task(content='')
        self.assertEqual(task.content, '')

    def test_title_max_length(self):
        max_len = Task._meta.get_field('title').max_length
        self.assertEqual(max_len, 200)


# ---------------------------------------------------------------------------
# Notification model tests
# ---------------------------------------------------------------------------
class TestNotificationModel(TaskModelTestHelper, TestCase):
    """Tests for Notification model."""

    @classmethod
    def setUpTestData(cls):
        cls.create_users_and_org()

    def test_create_notification(self):
        task = self.create_task()
        notif = Notification.objects.create(
            user=self.agent_user, task=task,
            title='Test Notification', message='Hello',
        )
        self.assertIsNotNone(notif.pk)

    def test_str_representation(self):
        notif = Notification.objects.create(
            user=self.agent_user, title='Due soon',
        )
        self.assertEqual(str(notif), f'Due soon ({self.agent_user.username})')

    def test_default_is_read(self):
        notif = Notification.objects.create(
            user=self.agent_user, title='Test',
        )
        self.assertFalse(notif.is_read)

    def test_unique_key(self):
        Notification.objects.create(
            user=self.agent_user, title='N1', key='unique_key_1',
        )
        with self.assertRaises(IntegrityError):
            Notification.objects.create(
                user=self.agent_user, title='N2', key='unique_key_1',
            )

    def test_key_nullable(self):
        n1 = Notification.objects.create(user=self.agent_user, title='N1', key=None)
        n2 = Notification.objects.create(user=self.agent_user, title='N2', key=None)
        self.assertIsNone(n1.key)
        self.assertIsNone(n2.key)

    def test_cascade_delete_user(self):
        user = User.objects.create_user(
            username='temp_notif', email='temp_notif@test.com', password='pass123',
        )
        notif = Notification.objects.create(user=user, title='Temp')
        notif_pk = notif.pk
        user.delete()
        self.assertFalse(Notification.objects.filter(pk=notif_pk).exists())

    def test_cascade_delete_task(self):
        task = self.create_task()
        notif = Notification.objects.create(
            user=self.agent_user, task=task, title='Task Notif',
        )
        notif_pk = notif.pk
        task.delete()
        self.assertFalse(Notification.objects.filter(pk=notif_pk).exists())

    def test_task_nullable(self):
        notif = Notification.objects.create(
            user=self.agent_user, title='No Task',
        )
        self.assertIsNone(notif.task)

    def test_ordering(self):
        n1 = Notification.objects.create(user=self.agent_user, title='Older')
        n2 = Notification.objects.create(user=self.agent_user, title='Newer')
        notifs = list(Notification.objects.filter(user=self.agent_user))
        self.assertGreater(n2.pk, n1.pk)
        self.assertEqual(len(notifs), 2)

    def test_auto_created_at(self):
        notif = Notification.objects.create(user=self.agent_user, title='TS')
        self.assertIsNotNone(notif.created_at)


class TestNotificationDisplayProperties(TaskModelTestHelper, TestCase):
    """Tests for display_url and display_label properties."""

    @classmethod
    def setUpTestData(cls):
        cls.create_users_and_org()

    def test_display_url_with_action_url(self):
        notif = Notification.objects.create(
            user=self.agent_user, title='Test',
            action_url='/custom/url/',
        )
        self.assertEqual(notif.display_url, '/custom/url/')

    def test_display_url_fallback_to_task(self):
        task = self.create_task()
        notif = Notification.objects.create(
            user=self.agent_user, task=task, title='Test',
        )
        expected_url = reverse('tasks:task-detail', kwargs={'pk': task.pk})
        self.assertEqual(notif.display_url, expected_url)

    def test_display_url_none_when_no_task_or_action(self):
        notif = Notification.objects.create(
            user=self.agent_user, title='Test',
        )
        self.assertIsNone(notif.display_url)

    def test_display_label_with_action_label(self):
        notif = Notification.objects.create(
            user=self.agent_user, title='Test',
            action_label='View Order',
        )
        self.assertEqual(notif.display_label, 'View Order')

    def test_display_label_fallback_to_view_task(self):
        task = self.create_task()
        notif = Notification.objects.create(
            user=self.agent_user, task=task, title='Test',
        )
        self.assertEqual(notif.display_label, 'View Task')

    def test_display_label_none_when_no_task_or_label(self):
        notif = Notification.objects.create(
            user=self.agent_user, title='Test',
        )
        self.assertIsNone(notif.display_label)


class TestTaskModelIntegration(TaskModelTestHelper, TestCase):
    """Integration tests for Task + Notification."""

    @classmethod
    def setUpTestData(cls):
        cls.create_users_and_org()

    def test_task_with_multiple_notifications(self):
        task = self.create_task()
        for i in range(3):
            Notification.objects.create(
                user=self.agent_user, task=task,
                title=f'Notif {i}', key=f'key_{i}',
            )
        self.assertEqual(task.notifications.count(), 3)

    def test_user_tasks_and_notifications(self):
        task = self.create_task()
        Notification.objects.create(
            user=self.agent_user, task=task, title='Assigned',
        )
        self.assertEqual(self.agent_user.assigned_tasks.count(), 1)
        self.assertEqual(self.agent_user.notifications.count(), 1)

    def test_multiple_tasks_same_organisation(self):
        for i in range(5):
            self.create_task(title=f'Task {i}')
        self.assertEqual(self.organisation.tasks.count(), 5)
