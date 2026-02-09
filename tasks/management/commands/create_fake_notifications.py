"""
Create fake notifications for testing (View Task, View Lead, View Order, View Product).
Usage: python manage.py create_fake_notifications [--user USERNAME]
If --user is omitted, uses the first superuser (or first user).
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.urls import reverse

from tasks.models import Notification, Task
from leads.models import Lead
from orders.models import orders
from ProductsAndStock.models import ProductsAndStock

User = get_user_model()


class Command(BaseCommand):
    help = 'Create fake notifications for testing (View Task, View Lead, View Order, View Product)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            default=None,
            help='Username to send notifications to (default: first superuser)',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Remove existing fake test notifications for this user before creating new ones',
        )

    def handle(self, *args, **options):
        username = options['user']
        clear = options['clear']

        if username:
            user = User.objects.filter(username=username).first()
            if not user:
                self.stderr.write(self.style.ERROR(f'User "{username}" not found.'))
                return
        else:
            user = User.objects.filter(is_superuser=True).first() or User.objects.first()
            if not user:
                self.stderr.write(self.style.ERROR('No user found in database.'))
                return

        self.stdout.write(f'Creating fake notifications for user: {user.username} (pk={user.pk})')

        # Optional: delete previous fake notifications for this user
        if clear:
            deleted, _ = Notification.objects.filter(
                user=user,
                key__startswith='fake_test_',
            ).delete()
            if deleted:
                self.stdout.write(self.style.WARNING(f'Removed {deleted} old fake notification(s).'))

        # Get first available task, lead, order, product for real URLs (or use pk=1)
        task = Task.objects.first()
        lead = Lead.objects.first()
        order = orders.objects.first()
        product = ProductsAndStock.objects.first()

        def make_notification(key_suffix, title, message, action_url, action_label, task_obj=None):
            key = f'fake_test_{key_suffix}_{user.pk}'
            n, created = Notification.objects.update_or_create(
                user=user,
                key=key,
                defaults={
                    'task': task_obj,
                    'title': title,
                    'message': message,
                    'action_url': action_url or '',
                    'action_label': action_label or '',
                    'is_read': False,
                },
            )
            return created

        created_count = 0

        # 1. View Task
        task_url = reverse('tasks:task-detail', kwargs={'pk': task.pk}) if task else '/tasks/1/'
        if make_notification(
            'task',
            ' [TEST] New task assigned to you: Sample Task',
            'A new task "Sample Task" (due soon) has been assigned to you.',
            task_url,
            'View Task',
            task_obj=task,
        ):
            created_count += 1
        self.stdout.write(f'  • View Task -> {task_url}')

        # 2. View Lead
        lead_url = reverse('leads:lead-detail', kwargs={'pk': lead.pk}) if lead else '/leads/1/'
        if make_notification(
            'lead',
            ' [TEST] New lead assigned to you',
            'Lead "Test Lead" has been assigned to you. Contact: test@example.com',
            lead_url,
            'View Lead',
        ):
            created_count += 1
        self.stdout.write(f'  • View Lead -> {lead_url}')

        # 3. View Order (order created)
        order_url = reverse('orders:order-detail', kwargs={'pk': order.pk}) if order else '/orders/order/1/'
        if make_notification(
            'order',
            ' [TEST] An order was created',
            'Order "Test Order" has been created.',
            order_url,
            'View Order',
        ):
            created_count += 1
        self.stdout.write(f'  • View Order -> {order_url}')

        # 4. View Product (stock alert)
        product_url = reverse('ProductsAndStock:ProductAndStock-detail', kwargs={'pk': product.pk}) if product else '/ProductsAndStock/1/'
        if make_notification(
            'product',
            ' [TEST] A stock alert was created',
            'Product "Sample Product": Low stock - check inventory.',
            product_url,
            'View Product',
        ):
            created_count += 1
        self.stdout.write(f'  • View Product -> {product_url}')

        self.stdout.write(self.style.SUCCESS(
            f'Done. {created_count} new fake notification(s) created. Open /tasks/notifications/ to see them.'
        ))
