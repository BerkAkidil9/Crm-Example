from django.core.management.base import BaseCommand
from ProductsAndStock.models import Category, SubCategory, ProductsAndStock


# Default category/subcategory for products when replacing (must exist in categories_data)
DEFAULT_CATEGORY_NAME = 'Products'
DEFAULT_SUBCATEGORY_NAME = 'Other'


class Command(BaseCommand):
    help = 'Create CRM-oriented categories and subcategories. Use --replace to remove old ones and apply only the new set.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--replace',
            action='store_true',
            help='Remove ALL old categories/subcategories and apply only the new CRM set. Existing products are moved to "Services" / "Other Services".',
        )

    def handle(self, *args, **options):
        # Simple set: 5 categories, 3-4 subcategories each
        categories_data = [
            {
                'name': 'Products',
                'description': 'Physical products',
                'icon': 'fas fa-box',
                'subcategories': [
                    {'name': 'Merchandise', 'description': 'Products and promotions'},
                    {'name': 'Inventory', 'description': 'Stock items'},
                    {'name': 'Other', 'description': 'Other'},
                ]
            },
            {
                'name': 'Services',
                'description': 'Services',
                'icon': 'fas fa-handshake',
                'subcategories': [
                    {'name': 'Consulting', 'description': 'Consulting'},
                    {'name': 'Support', 'description': 'Support'},
                    {'name': 'Training', 'description': 'Training'},
                    {'name': 'Other', 'description': 'Other'},
                ]
            },
            {
                'name': 'Software',
                'description': 'Software and digital',
                'icon': 'fas fa-laptop-code',
                'subcategories': [
                    {'name': 'Licenses', 'description': 'Licenses'},
                    {'name': 'SaaS', 'description': 'Cloud / subscription'},
                    {'name': 'Other', 'description': 'Other'},
                ]
            },
            {
                'name': 'Subscriptions',
                'description': 'Subscriptions and recurring',
                'icon': 'fas fa-sync-alt',
                'subcategories': [
                    {'name': 'Monthly', 'description': 'Monthly'},
                    {'name': 'Annual', 'description': 'Annual'},
                    {'name': 'Other', 'description': 'Other'},
                ]
            },
            {
                'name': 'Other',
                'description': 'Other categories',
                'icon': 'fas fa-folder',
                'subcategories': [
                    {'name': 'General', 'description': 'General'},
                    {'name': 'Misc', 'description': 'Miscellaneous'},
                ]
            },
        ]

        new_category_names = {c['name'] for c in categories_data}
        new_subcategory_keys = {
            (c['name'], sc['name'])
            for c in categories_data
            for sc in c['subcategories']
        }

        # 1) Create all new CRM categories and subcategories
        created_categories = 0
        created_subcategories = 0
        default_category = None
        default_subcategory = None

        for category_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=category_data['name'],
                defaults={
                    'description': category_data['description'],
                    'icon': category_data['icon']
                }
            )
            if category.name == DEFAULT_CATEGORY_NAME:
                default_category = category
            if created:
                created_categories += 1
                self.stdout.write(self.style.SUCCESS(f'Created category: {category.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Category already exists: {category.name}'))

            for subcat_data in category_data['subcategories']:
                subcategory, created = SubCategory.objects.get_or_create(
                    name=subcat_data['name'],
                    category=category,
                    defaults={'description': subcat_data['description']}
                )
                if category.name == DEFAULT_CATEGORY_NAME and subcategory.name == DEFAULT_SUBCATEGORY_NAME:
                    default_subcategory = subcategory
                if created:
                    created_subcategories += 1
                    self.stdout.write(self.style.SUCCESS(f'  Created subcategory: {subcategory.name}'))

        if options.get('replace'):
            if not default_category or not default_subcategory:
                self.stdout.write(
                    self.style.ERROR(
                        f'Default "{DEFAULT_CATEGORY_NAME}" / "{DEFAULT_SUBCATEGORY_NAME}" not found. Cannot replace.'
                    )
                )
                return

            # 2) Point all products to the default new category/subcategory
            updated = ProductsAndStock.objects.exclude(
                category=default_category,
                subcategory=default_subcategory,
            ).update(category=default_category, subcategory=default_subcategory)
            if updated:
                self.stdout.write(
                    self.style.WARNING(f'Updated {updated} product(s) to "{DEFAULT_CATEGORY_NAME}" / "{DEFAULT_SUBCATEGORY_NAME}".')
                )

            # 3) Delete subcategories that are not in the new CRM set
            deleted_sub = 0
            for sub in SubCategory.objects.select_related('category').all():
                key = (sub.category.name, sub.name)
                if key not in new_subcategory_keys:
                    sub.delete()
                    deleted_sub += 1
            if deleted_sub:
                self.stdout.write(self.style.WARNING(f'Removed {deleted_sub} old subcategories.'))

            # 4) Delete categories that are not in the new CRM set
            deleted_cat = 0
            for cat in Category.objects.all():
                if cat.name not in new_category_names:
                    cat.delete()
                    deleted_cat += 1
            if deleted_cat:
                self.stdout.write(self.style.WARNING(f'Removed {deleted_cat} old categories.'))

        self.stdout.write(
            self.style.SUCCESS(
                f'\nDone. Created {created_categories} categories and {created_subcategories} subcategories.'
            )
        )
