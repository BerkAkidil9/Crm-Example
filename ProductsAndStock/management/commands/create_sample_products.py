"""
Organisor adına her subcategory için örnek ürün oluşturur.
Kullanım: python manage.py create_sample_products [--username ORGANISOR_USERNAME]
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from leads.models import UserProfile
from ProductsAndStock.models import Category, SubCategory, ProductsAndStock


# Her (category_name, subcategory_name) için: (product_name max 20 char, description, price, cost, quantity, min_stock)
PRODUCTS_BY_SUBCATEGORY = {
    ('Products', 'Merchandise'): {
        'product_name': 'Merchandise Pack',
        'product_description': 'Promosyon ve merchandising ürün paketi.',
        'product_price': 49.99,
        'cost_price': 25.00,
        'product_quantity': 100,
        'minimum_stock_level': 20,
    },
    ('Products', 'Inventory'): {
        'product_name': 'Inventory Item',
        'product_description': 'Stok takibi yapılan standart envanter kalemi.',
        'product_price': 29.99,
        'cost_price': 15.00,
        'product_quantity': 200,
        'minimum_stock_level': 50,
    },
    ('Products', 'Other'): {
        'product_name': 'Product Other',
        'product_description': 'Diğer fiziksel ürün kategorisi.',
        'product_price': 19.99,
        'cost_price': 10.00,
        'product_quantity': 80,
        'minimum_stock_level': 15,
    },
    ('Services', 'Consulting'): {
        'product_name': 'Consulting Hour',
        'product_description': 'Danışmanlık hizmeti saatlik birim.',
        'product_price': 150.00,
        'cost_price': 0,
        'product_quantity': 999,
        'minimum_stock_level': 0,
    },
    ('Services', 'Support'): {
        'product_name': 'Support Ticket',
        'product_description': 'Teknik destek bileti / destek paketi.',
        'product_price': 75.00,
        'cost_price': 0,
        'product_quantity': 999,
        'minimum_stock_level': 0,
    },
    ('Services', 'Training'): {
        'product_name': 'Training Session',
        'product_description': 'Eğitim oturumu veya workshop.',
        'product_price': 200.00,
        'cost_price': 0,
        'product_quantity': 50,
        'minimum_stock_level': 0,
    },
    ('Services', 'Other'): {
        'product_name': 'Service Other',
        'product_description': 'Diğer hizmet türü.',
        'product_price': 99.00,
        'cost_price': 0,
        'product_quantity': 999,
        'minimum_stock_level': 0,
    },
    ('Software', 'Licenses'): {
        'product_name': 'License Key',
        'product_description': 'Yazılım lisans anahtarı.',
        'product_price': 299.00,
        'cost_price': 120.00,
        'product_quantity': 50,
        'minimum_stock_level': 10,
    },
    ('Software', 'SaaS'): {
        'product_name': 'SaaS Plan',
        'product_description': 'Bulut / abonelik tabanlı yazılım planı.',
        'product_price': 49.00,
        'cost_price': 0,
        'product_quantity': 999,
        'minimum_stock_level': 0,
    },
    ('Software', 'Other'): {
        'product_name': 'Software Other',
        'product_description': 'Diğer yazılım veya dijital ürün.',
        'product_price': 79.00,
        'cost_price': 0,
        'product_quantity': 999,
        'minimum_stock_level': 0,
    },
    ('Subscriptions', 'Monthly'): {
        'product_name': 'Monthly Plan',
        'product_description': 'Aylık abonelik planı.',
        'product_price': 19.99,
        'cost_price': 0,
        'product_quantity': 999,
        'minimum_stock_level': 0,
    },
    ('Subscriptions', 'Annual'): {
        'product_name': 'Annual Plan',
        'product_description': 'Yıllık abonelik planı.',
        'product_price': 199.00,
        'cost_price': 0,
        'product_quantity': 999,
        'minimum_stock_level': 0,
    },
    ('Subscriptions', 'Other'): {
        'product_name': 'Subscr Other',
        'product_description': 'Diğer abonelik türü.',
        'product_price': 59.00,
        'cost_price': 0,
        'product_quantity': 999,
        'minimum_stock_level': 0,
    },
    ('Other', 'General'): {
        'product_name': 'General Item',
        'product_description': 'Genel kategorideki kalem.',
        'product_price': 39.99,
        'cost_price': 20.00,
        'product_quantity': 60,
        'minimum_stock_level': 10,
    },
    ('Other', 'Misc'): {
        'product_name': 'Misc Product',
        'product_description': 'Çeşitli / diğer ürün.',
        'product_price': 24.99,
        'cost_price': 12.00,
        'product_quantity': 40,
        'minimum_stock_level': 5,
    },
}


class Command(BaseCommand):
    help = 'Organisor adına her subcategory için örnek ürün oluşturur.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default=None,
            help='Organisor kullanıcı adı. Verilmezse ilk organisor kullanılır.',
        )

    def handle(self, *args, **options):
        username = options.get('username')

        if username:
            try:
                profile = UserProfile.objects.get(user__username=username)
                if not profile.user.is_organisor:
                    self.stdout.write(
                        self.style.ERROR(f'"{username}" organisor değil. Organisor kullanıcı adı girin.')
                    )
                    return
            except UserProfile.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Kullanıcı bulunamadı: {username}'))
                return
        else:
            profile = UserProfile.objects.filter(user__is_organisor=True).first()
            if not profile:
                self.stdout.write(self.style.ERROR('Hiç organisor (UserProfile) bulunamadı.'))
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
                        self.style.WARNING(f'Atlandı (kategori/alt kategori yok): {cat_name} / {subcat_name}')
                    )
                    skipped += 1
                    continue

                name = data['product_name']
                if ProductsAndStock.objects.filter(organisation=organisation, product_name=name).exists():
                    self.stdout.write(self.style.WARNING(f'Zaten var: {name}'))
                    skipped += 1
                    continue

                ProductsAndStock.objects.create(
                    organisation=organisation,
                    category=category,
                    subcategory=subcategory,
                    **data,
                )
                created += 1
                self.stdout.write(self.style.SUCCESS(f'Oluşturuldu: {name} ({cat_name} / {subcat_name})'))

        self.stdout.write(
            self.style.SUCCESS(f'\nToplam: {created} ürün oluşturuldu, {skipped} atlandı.')
        )
