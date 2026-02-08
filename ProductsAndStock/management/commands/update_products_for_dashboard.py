"""
Tum urunlerde: cost_price 0 olmasin, minimum_stock_level 0 olmasin.
Ayrica bazi urunleri dashboard'da her senaryonun gorunmesi icin gunceller:
- Out of stock, Low stock (critical/high), Overstock, normal stok.
Kullanim: python manage.py update_products_for_dashboard
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from ProductsAndStock.models import ProductsAndStock


# product_name -> (product_quantity, minimum_stock_level) for dashboard variety
# Bu urunler bu degerlere cekilir; diger tum urunlerde sadece cost_price ve min_stock 0 olmasin diye duzeltilir.
DASHBOARD_SCENARIOS = {
    # OUT_OF_STOCK (quantity=0)
    'Merchandise Pack': (0, 20),
    # LOW_STOCK - critical (qty <= min/2)
    'Inventory Item': (5, 20),
    # LOW_STOCK - high (qty <= min but > min/2)
    'Product Other': (12, 20),
    # OVERSTOCK (qty > min*10)
    'Support Ticket': (500, 10),
    'License Key': (150, 10),
    # Normal in-stock
    'Consulting Hour': (999, 50),
    'Training Session': (50, 10),
    'Service Other': (999, 50),
    'SaaS Plan': (999, 20),
    'Software Other': (999, 20),
    'Monthly Plan': (999, 30),
    'Annual Plan': (999, 20),
    'Subscr Other': (999, 20),
    'General Item': (60, 10),
    'Misc Product': (40, 5),
}


class Command(BaseCommand):
    help = 'Tum urunlerde cost_price ve minimum_stock_level 0 yapma; bazi urunleri dashboard senaryolarina gore gunceller.'

    def handle(self, *args, **options):
        updated_count = 0
        with transaction.atomic():
            for product in ProductsAndStock.objects.all():
                changed = False
                # 1) cost_price 0 ise urun fiyatinin %40'i yap
                if product.cost_price == 0:
                    product.cost_price = round(product.product_price * 0.4, 2)
                    changed = True
                # 2) minimum_stock_level 0 ise 10 yap (veya senaryoda belirtilen)
                if product.minimum_stock_level == 0:
                    product.minimum_stock_level = 10
                    changed = True
                # 3) Bu urun dashboard senaryosunda varsa quantity ve min_stock oraya cek
                if product.product_name in DASHBOARD_SCENARIOS:
                    qty, min_stock = DASHBOARD_SCENARIOS[product.product_name]
                    if product.product_quantity != qty or product.minimum_stock_level != min_stock:
                        product.product_quantity = qty
                        product.minimum_stock_level = min_stock
                        changed = True
                if changed:
                    product.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Updated: {product.product_name} (qty={product.product_quantity}, min={product.minimum_stock_level}, cost={product.cost_price})"
                        )
                    )
        self.stdout.write(self.style.SUCCESS(f"\nToplam {updated_count} urun guncellendi."))
        self.stdout.write(
            self.style.WARNING(
                "Dashboard'da kontrol edin: Out of stock (Merchandise Pack), Low stock (Inventory Item, Product Other), "
                "Overstock (Support Ticket, License Key), Recent Alerts, Stock Recommendations."
            )
        )
