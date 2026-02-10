"""
Send email and in-app notification when a task's end date is approaching.
Run daily via cron: python manage.py check_task_deadlines
Reminds 3 days before and 1 day before deadline (only incomplete tasks).
"""
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.urls import reverse

from tasks.models import Task, Notification


class Command(BaseCommand):
    help = 'Send deadline reminders (email + notification) for tasks ending in 1 or 3 days'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            nargs='+',
            type=int,
            default=[1, 3],
            help='Days before deadline to send reminder (default: 1 3)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Only print what would be sent, do not send',
        )

    def handle(self, *args, **options):
        days_list = options['days']
        dry_run = options['dry_run']
        today = timezone.now().date()

        for days in days_list:
            target_date = today + timedelta(days=days)
            tasks = Task.objects.filter(
                end_date=target_date,
                status__in=['pending', 'in_progress'],
            ).select_related('assigned_to', 'organisation')

            for task in tasks:
                key = f"task_deadline_{task.id}_{days}d"
                if Notification.objects.filter(key=key).exists():
                    continue

                user = task.assigned_to
                if not user.email:
                    continue

                if days == 1:
                    title = f"Task due tomorrow: {task.title}"
                else:
                    title = f"Task due in {days} days: {task.title}"

                message = (
                    f"Hello {user.get_full_name() or user.username},\n\n"
                    f"Reminder: the following task is due in {days} day(s).\n\n"
                    f"Task: {task.title}\n"
                    f"End date: {task.end_date}\n"
                    f"Priority: {task.get_priority_display()}\n\n"
                    f"View task: {settings.SITE_URL}/tasks/{task.id}/\n\n"
                    f"Darkenyas CRM"
                )

                if dry_run:
                    self.stdout.write(f"Would send to {user.email}: {title}")
                    continue

                try:
                    send_mail(
                        title,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],
                        fail_silently=False,
                    )
                except Exception as e:
                    self.stderr.write(f"Email failed for task {task.id}: {e}")
                    continue

                task_url = reverse('tasks:task-detail', kwargs={'pk': task.pk})
                Notification.objects.create(
                    user=user,
                    task=task,
                    title=title,
                    message=message,
                    key=key,
                    action_url=task_url,
                    action_label='View Task',
                )
                self.stdout.write(self.style.SUCCESS(f"Sent reminder for task {task.id} to {user.email}"))
