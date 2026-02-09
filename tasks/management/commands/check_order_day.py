"""
Notify organisor and agent when an order's order_day (delivery/completion date) is today.
Run daily via cron: python manage.py check_order_day
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.urls import reverse

from leads.models import Lead
from orders.models import orders
from tasks.models import Notification


class Command(BaseCommand):
    help = 'Notify organisor and agent when order day (sale completion) is today'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Only print what would be sent',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        today = timezone.now().date()

        # Orders whose order_day is today (date part) and not cancelled
        order_list = orders.objects.filter(
            is_cancelled=False,
            order_day__date=today,
        ).select_related('organisation__user').prefetch_related('lead')

        for order in order_list:
            users_to_notify = [order.organisation.user]
            if order.lead_id:
                lead = Lead.objects.filter(pk=order.lead_id).select_related('agent__user').first()
                if lead and lead.agent:
                    users_to_notify.append(lead.agent.user)

            title = "Sale completed"
            message = f'Order "{order.order_name}" is due today (order day). Sale completed.'

            for user in set(users_to_notify):
                key = f"order_day_{order.id}_{user.id}_{today.isoformat()}"
                if Notification.objects.filter(key=key).exists():
                    continue
                if dry_run:
                    self.stdout.write(f"Would notify {user.username}: {title} - {order.order_name}")
                    continue
                order_url = reverse('orders:order-detail', kwargs={'pk': order.pk})
                Notification.objects.create(
                    user=user,
                    task=None,
                    title=title,
                    message=message,
                    key=key,
                    action_url=order_url,
                    action_label='View Order',
                )
                self.stdout.write(self.style.SUCCESS(f"Notified {user.username}: {title} - {order.order_name}"))

        if not order_list and not dry_run:
            self.stdout.write("No orders with order_day today.")
