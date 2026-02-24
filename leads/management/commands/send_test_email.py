"""
Test email sending. Run on Render Shell to debug: python manage.py send_test_email your@email.com
"""
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings


class Command(BaseCommand):
    help = 'Send a test email to verify Gmail API / SMTP configuration'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Recipient email address')

    def handle(self, *args, **options):
        to_email = options['email']
        backend = getattr(settings, 'EMAIL_BACKEND', 'unknown')
        self.stdout.write(f'Email backend: {backend}')
        if 'gmailapi' in backend.lower():
            has_id = bool(getattr(settings, 'GMAIL_API_CLIENT_ID', None))
            has_secret = bool(getattr(settings, 'GMAIL_API_CLIENT_SECRET', None))
            has_token = bool(getattr(settings, 'GMAIL_API_REFRESH_TOKEN', None))
            self.stdout.write(f'GMAIL_API_CLIENT_ID: {"set" if has_id else "MISSING"}')
            self.stdout.write(f'GMAIL_API_CLIENT_SECRET: {"set" if has_secret else "MISSING"}')
            self.stdout.write(f'GMAIL_API_REFRESH_TOKEN: {"set" if has_token else "MISSING"}')
            if not (has_id and has_secret and has_token):
                self.stderr.write(self.style.ERROR('Gmail API credentials missing. Add them in Render Dashboard.'))
                return
        self.stdout.write(f'Sending test email to {to_email}...')
        try:
            send_mail(
                subject='CRM Test Email',
                message='This is a test email from your CRM. If you receive this, email is working.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[to_email],
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS('Email sent successfully!'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Email failed: {e}'))
