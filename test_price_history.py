#!/usr/bin/env python
import os
import django

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djcrm.settings')
django.setup()

from ProductsAndStock.models import ProductsAndStock, PriceHistory
from leads.models import User

def test_price_history():
    print("=== Fiyat Geçmişi Testi ===")
    
    # İlk ürünü al
    product = ProductsAndStock.objects.first()
    if not product:
        print("❌ Ürün bulunamadı!")
        return
    
    print(f"📦 Ürün: {product.product_name}")
    print(f"💰 Mevcut fiyat: ${product.product_price}")
    
    # Mevcut price history sayısı
    initial_count = product.price_history.count()
    print(f"📊 Başlangıç price history sayısı: {initial_count}")
    
    # Fiyatı değiştir
    old_price = product.product_price
    new_price = old_price + 10
    product.product_price = new_price
    
    print(f"🔄 Fiyat değiştiriliyor: ${old_price} -> ${new_price}")
    product.save()
    
    # Price history kontrol et
    final_count = product.price_history.count()
    print(f"📊 Son price history sayısı: {final_count}")
    
    if final_count > initial_count:
        latest = product.price_history.first()
        print(f"✅ Yeni kayıt oluştu: {latest.old_price} -> {latest.new_price}")
        print(f"📝 Değişiklik türü: {latest.get_change_type_display()}")
        print(f"📅 Tarih: {latest.created_at}")
    else:
        print("❌ Price history kaydı oluşmamış!")
    
    # Stock movement kontrol et
    stock_movements = product.stock_movements.count()
    print(f"📦 Stock movement sayısı: {stock_movements}")
    
    if stock_movements > 0:
        latest_movement = product.stock_movements.first()
        print(f"📈 Son stock movement: {latest_movement.get_movement_type_display()}")
        print(f"📊 Miktar: {latest_movement.quantity_before} -> {latest_movement.quantity_after}")

if __name__ == "__main__":
    test_price_history()
