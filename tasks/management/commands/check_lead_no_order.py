"""
Notify agent when their lead has not placed any order in the last 1 month.
Run periodically (e.g. weekly): python manage.py check_lead_no_order
Uses a key per lead per month to avoid duplicate notifications.
"""
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Max
from django.urls import reverse

from leads.models import Lead
from orders.models import orders
from tasks.models import Notification


class Command(BaseCommand):
    help = 'Notify agents whose leads have not placed an order in the last 30 days'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Only print what would be sent, do not create notifications',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        now = timezone.now()
        cutoff = now - timedelta(days=30)
        year_month = now.strftime('%Y-%m')

        # Leads that have an agent
        leads = Lead.objects.filter(agent__isnull=False).select_related('agent', 'agent__user')

        for lead in leads:
            # Last non-cancelled order for this lead
            last_order = (
                orders.objects.filter(lead=lead, is_cancelled=False)
                .aggregate(last=Max('creation_date'))
            )
            last_order_date = last_order.get('last')

            no_order_in_month = False
            if last_order_date is None:
                # Never ordered: notify if lead was added more than 30 days ago
                if lead.date_added and lead.date_added < cutoff:
                    no_order_in_month = True
            else:
                if last_order_date < cutoff:
                    no_order_in_month = True

            if not no_order_in_month:
                continue

            key = f"lead_no_order_{lead.id}_{year_month}"
            if Notification.objects.filter(key=key).exists():
                continue

            user = lead.agent.user
            lead_name = f"{lead.first_name} {lead.last_name}".strip() or lead.email
            title = "Customer has not placed an order in 1 month"
            message = (
                f'Lead "{lead_name}" ({lead.email}) has not placed any order in the last 30 days. '
                f'Consider following up.'
            )

            if dry_run:
                self.stdout.write(f"Would notify {user.username}: {title} for lead {lead_name}")
                continue

            lead_url = reverse('leads:lead-detail', kwargs={'pk': lead.pk})
            Notification.objects.create(
                user=user,
                task=None,
                title=title,
                message=message,
                key=key,
                action_url=lead_url,
                action_label='View Lead',
            )
            self.stdout.write(self.style.SUCCESS(f"Notified {user.username} for lead {lead_name} (no order in 30 days)"))
