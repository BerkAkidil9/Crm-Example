"""
Moves products from one organisor's organisation (by email) to another's.
Or moves products under admin to the organisor with the given email.

Usage:
  python manage.py reassign_products_to_organisor --to-email crmtest0923+organisor@gmail.com
  python manage.py reassign_products_to_organisor --to-email crmtest0923+organisor@gmail.com --from-username admin
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from leads.models import UserProfile
from ProductsAndStock.models import ProductsAndStock

User = get_user_model()


class Command(BaseCommand):
    help = 'Move products from one organisor organisation to another (--to-email for target organisor).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--to-email',
            type=str,
            required=True,
            help='Email of the organisor to move products to (e.g. crmtest0923+organisor@gmail.com)',
        )
        parser.add_argument(
            '--from-username',
            type=str,
            default='admin',
            help='Username of current owner to take products from (default: admin)',
        )

    def handle(self, *args, **options):
        to_email = options['to_email'].strip()
        from_username = options['from_username'].strip()

        # Target: organisor UserProfile by email
        try:
            to_user = User.objects.get(email=to_email)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Email not found: {to_email}'))
            return

        try:
            to_profile = UserProfile.objects.get(user=to_user)
        except UserProfile.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'No UserProfile for this user: {to_email}'))
            return

        if not to_user.is_organisor:
            self.stdout.write(self.style.WARNING(f'"{to_email}" is not an organisor; moving anyway.'))

        # Source: UserProfile by from_username (e.g. admin)
        try:
            from_user = User.objects.get(username=from_username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User not found: {from_username}'))
            return

        try:
            from_profile = UserProfile.objects.get(user=from_user)
        except UserProfile.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'UserProfile not found: {from_username}'))
            return

        if from_profile.pk == to_profile.pk:
            self.stdout.write(self.style.WARNING('Source and target are the same organisor; no move.'))
            return

        products = ProductsAndStock.objects.filter(organisation=from_profile)
        count = products.count()
        if count == 0:
            self.stdout.write(self.style.WARNING(f'No products to move in "{from_username}" organisation.'))
            return

        products.update(organisation=to_profile)
        self.stdout.write(
            self.style.SUCCESS(
                f'{count} product(s) moved from "{from_username}" to {to_email} ({to_user.username}) organisation.'
            )
        )
