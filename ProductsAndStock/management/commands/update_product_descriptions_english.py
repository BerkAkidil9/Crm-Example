"""
Mevcut ornek urunlerin (product_name ile eslesen) description alanini Ingilizce metinle gunceller.
Kullanım: python manage.py update_product_descriptions_english
"""
from django.core.management.base import BaseCommand
from ProductsAndStock.models import ProductsAndStock
from ProductsAndStock.management.commands.create_sample_products import PRODUCTS_BY_SUBCATEGORY

# product_name -> English description
NAME_TO_EN_DESCRIPTION = {
    data['product_name']: data['product_description']
    for data in PRODUCTS_BY_SUBCATEGORY.values()
}


class Command(BaseCommand):
    help = "Sample urunlerin aciklamalarini Ingilizce'ye gunceller."

    def handle(self, *args, **options):
        updated = 0
        for name, desc in NAME_TO_EN_DESCRIPTION.items():
            count = ProductsAndStock.objects.filter(product_name=name).update(product_description=desc)
            if count:
                updated += count
                self.stdout.write(self.style.SUCCESS(f'Updated: {name} ({count} product(s))'))
        self.stdout.write(self.style.SUCCESS(f'\nToplam {updated} urun aciklamasi Ingilizce yapildi.'))
