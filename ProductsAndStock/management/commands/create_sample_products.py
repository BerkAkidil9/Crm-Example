"""
Create sample products for each subcategory on behalf of an organisor.
Usage: python manage.py create_sample_products [--username ORGANISOR_USERNAME]
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from leads.models import UserProfile
from ProductsAndStock.models import Category, SubCategory, ProductsAndStock


# (category_name, subcategory_name) -> product_name max 20 char, description in English, price, cost, quantity, min_stock
PRODUCTS_BY_SUBCATEGORY = {
    ('Products', 'Merchandise'): {
        'product_name': 'Merchandise Pack',
        'product_description': 'Promotional and merchandising product pack.',
        'product_price': 49.99,
        'cost_price': 25.00,
        'product_quantity': 100,
        'minimum_stock_level': 20,
    },
    ('Products', 'Inventory'): {
        'product_name': 'Inventory Item',
        'product_description': 'Standard inventory item for stock tracking.',
        'product_price': 29.99,
        'cost_price': 15.00,
        'product_quantity': 200,
        'minimum_stock_level': 50,
    },
    ('Products', 'Other'): {
        'product_name': 'Product Other',
        'product_description': 'Other physical product category.',
        'product_price': 19.99,
        'cost_price': 10.00,
        'product_quantity': 80,
        'minimum_stock_level': 15,
    },
    ('Services', 'Consulting'): {
        'product_name': 'Consulting Hour',
        'product_description': 'Consulting service per hour.',
        'product_price': 150.00,
        'cost_price': 0,
        'product_quantity': 999,
        'minimum_stock_level': 0,
    },
    ('Services', 'Support'): {
        'product_name': 'Support Ticket',
        'product_description': 'Technical support ticket or support package.',
        'product_price': 75.00,
        'cost_price': 0,
        'product_quantity': 999,
        'minimum_stock_level': 0,
    },
    ('Services', 'Training'): {
        'product_name': 'Training Session',
        'product_description': 'Training session or workshop.',
        'product_price': 200.00,
        'cost_price': 0,
        'product_quantity': 50,
        'minimum_stock_level': 0,
    },
    ('Services', 'Other'): {
        'product_name': 'Service Other',
        'product_description': 'Other service type.',
        'product_price': 99.00,
        'cost_price': 0,
        'product_quantity': 999,
        'minimum_stock_level': 0,
    },
    ('Software', 'Licenses'): {
        'product_name': 'License Key',
        'product_description': 'Software license key.',
        'product_price': 299.00,
        'cost_price': 120.00,
        'product_quantity': 50,
        'minimum_stock_level': 10,
    },
    ('Software', 'SaaS'): {
        'product_name': 'SaaS Plan',
        'product_description': 'Cloud or subscription-based software plan.',
        'product_price': 49.00,
        'cost_price': 0,
        'product_quantity': 999,
        'minimum_stock_level': 0,
    },
    ('Software', 'Other'): {
        'product_name': 'Software Other',
        'product_description': 'Other software or digital product.',
        'product_price': 79.00,
        'cost_price': 0,
        'product_quantity': 999,
        'minimum_stock_level': 0,
    },
    ('Subscriptions', 'Monthly'): {
        'product_name': 'Monthly Plan',
        'product_description': 'Monthly subscription plan.',
        'product_price': 19.99,
        'cost_price': 0,
        'product_quantity': 999,
        'minimum_stock_level': 0,
    },
    ('Subscriptions', 'Annual'): {
        'product_name': 'Annual Plan',
        'product_description': 'Annual subscription plan.',
        'product_price': 199.00,
        'cost_price': 0,
        'product_quantity': 999,
        'minimum_stock_level': 0,
    },
    ('Subscriptions', 'Other'): {
        'product_name': 'Subscr Other',
        'product_description': 'Other subscription type.',
        'product_price': 59.00,
        'cost_price': 0,
        'product_quantity': 999,
        'minimum_stock_level': 0,
    },
    ('Other', 'General'): {
        'product_name': 'General Item',
        'product_description': 'General category item.',
        'product_price': 39.99,
        'cost_price': 20.00,
        'product_quantity': 60,
        'minimum_stock_level': 10,
    },
    ('Other', 'Misc'): {
        'product_name': 'Misc Product',
        'product_description': 'Miscellaneous or other product.',
        'product_price': 24.99,
        'cost_price': 12.00,
        'product_quantity': 40,
        'minimum_stock_level': 5,
    },
}


class Command(BaseCommand):
    help = 'Create sample products for each subcategory on behalf of an organisor.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default=None,
            help='Organisor username. If not provided, first organisor is used.',
        )

    def handle(self, *args, **options):
        username = options.get('username')

        if username:
            try:
                profile = UserProfile.objects.get(user__username=username)
                if not profile.user.is_organisor:
                    self.stdout.write(
                        self.style.ERROR(f'"{username}" is not an organisor. Enter an organisor username.')
                    )
                    return
            except UserProfile.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'User not found: {username}'))
                return
        else:
            profile = UserProfile.objects.filter(user__is_organisor=True).first()
            if not profile:
                self.stdout.write(self.style.ERROR('No organisor (UserProfile) found.'))
                return

        organisation = profile
        self.stdout.write(f'Organisation: {organisation} (user: {organisation.user.username})')

        created = 0
        skipped = 0

        with transaction.atomic():
            for (cat_name, subcat_name), data in PRODUCTS_BY_SUBCATEGORY.items():
                try:
                    category = Category.objects.get(name=cat_name)
                    subcategory = SubCategory.objects.get(category=category, name=subcat_name)
                except (Category.DoesNotExist, SubCategory.DoesNotExist):
                    self.stdout.write(
                        self.style.WARNING(f'Skipped (category/subcategory missing): {cat_name} / {subcat_name}')
                    )
                    skipped += 1
                    continue

                name = data['product_name']
                if ProductsAndStock.objects.filter(organisation=organisation, product_name=name).exists():
                    self.stdout.write(self.style.WARNING(f'Already exists: {name}'))
                    skipped += 1
                    continue

                ProductsAndStock.objects.create(
                    organisation=organisation,
                    category=category,
                    subcategory=subcategory,
                    **data,
                )
                created += 1
                self.stdout.write(self.style.SUCCESS(f'Created: {name} ({cat_name} / {subcat_name})'))

        self.stdout.write(
            self.style.SUCCESS(f'\nTotal: {created} products created, {skipped} skipped.')
        )
