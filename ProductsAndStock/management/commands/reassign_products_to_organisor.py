"""
Belirli bir organisorun (email ile) organizasyonundaki ürünleri başka bir organisorun
organizasyonuna taşır. Veya admin altındaki ürünleri verilen email'deki organisora taşır.

Kullanım:
  python manage.py reassign_products_to_organisor --to-email crmtest0923+organisor@gmail.com
  python manage.py reassign_products_to_organisor --to-email crmtest0923+organisor@gmail.com --from-username admin
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from leads.models import UserProfile
from ProductsAndStock.models import ProductsAndStock

User = get_user_model()


class Command(BaseCommand):
    help = 'Ürünleri bir organisor organizasyonundan diğerine taşır (--to-email ile hedef organisor).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--to-email',
            type=str,
            required=True,
            help='Ürünlerin taşınacağı organisorun email adresi (örn: crmtest0923+organisor@gmail.com)',
        )
        parser.add_argument(
            '--from-username',
            type=str,
            default='admin',
            help='Ürünlerin alınacağı mevcut sahip kullanıcı adı (varsayılan: admin)',
        )

    def handle(self, *args, **options):
        to_email = options['to_email'].strip()
        from_username = options['from_username'].strip()

        # Hedef: email ile organisor UserProfile
        try:
            to_user = User.objects.get(email=to_email)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Email bulunamadı: {to_email}'))
            return

        try:
            to_profile = UserProfile.objects.get(user=to_user)
        except UserProfile.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Bu kullanıcıya ait UserProfile yok: {to_email}'))
            return

        if not to_user.is_organisor:
            self.stdout.write(self.style.WARNING(f'"{to_email}" organisor değil; yine de taşıma yapılıyor.'))

        # Kaynak: from_username ile UserProfile (örn. admin)
        try:
            from_user = User.objects.get(username=from_username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Kullanıcı bulunamadı: {from_username}'))
            return

        try:
            from_profile = UserProfile.objects.get(user=from_user)
        except UserProfile.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'UserProfile bulunamadı: {from_username}'))
            return

        if from_profile.pk == to_profile.pk:
            self.stdout.write(self.style.WARNING('Kaynak ve hedef aynı organisor; taşıma yapılmadı.'))
            return

        products = ProductsAndStock.objects.filter(organisation=from_profile)
        count = products.count()
        if count == 0:
            self.stdout.write(self.style.WARNING(f'"{from_username}" organizasyonunda taşınacak ürün yok.'))
            return

        products.update(organisation=to_profile)
        self.stdout.write(
            self.style.SUCCESS(
                f'{count} urun "{from_username}" -> {to_email} ({to_user.username}) organizasyonuna tasindi.'
            )
        )
