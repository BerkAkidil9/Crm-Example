#!/usr/bin/env python
import os
import django

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djcrm.settings')
django.setup()

from ProductsAndStock.models import ProductsAndStock, PriceHistory
from leads.models import User

def test_price_history():
    print("=== Price History Test ===")
    
    # Get first product
    product = ProductsAndStock.objects.first()
    if not product:
        print("❌ No product found!")
        return
    
    print(f"📦 Product: {product.product_name}")
    print(f"💰 Current price: ${product.product_price}")
    
    # Current price history count
    initial_count = product.price_history.count()
    print(f"📊 Initial price history count: {initial_count}")
    
    # Change price
    old_price = product.product_price
    new_price = old_price + 10
    product.product_price = new_price
    
    print(f"🔄 Changing price: ${old_price} -> ${new_price}")
    product.save()
    
    # Check price history
    final_count = product.price_history.count()
    print(f"📊 Final price history count: {final_count}")
    
    if final_count > initial_count:
        latest = product.price_history.first()
        print(f"✅ New record created: {latest.old_price} -> {latest.new_price}")
        print(f"📝 Change type: {latest.get_change_type_display()}")
        print(f"📅 Date: {latest.created_at}")
    else:
        print("❌ No price history record was created!")
    
    # Check stock movement
    stock_movements = product.stock_movements.count()
    print(f"📦 Stock movement count: {stock_movements}")
    
    if stock_movements > 0:
        latest_movement = product.stock_movements.first()
        print(f"📈 Latest stock movement: {latest_movement.get_movement_type_display()}")
        print(f"📊 Quantity: {latest_movement.quantity_before} -> {latest_movement.quantity_after}")

if __name__ == "__main__":
    test_price_history()
