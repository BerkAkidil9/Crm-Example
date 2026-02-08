from django.db import models
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from leads.models import User, UserProfile, Lead
from ProductsAndStock.models import ProductsAndStock, StockMovement
from django.utils import timezone

class orders(models.Model):
    order_day = models.DateTimeField()
    order_name = models.CharField(max_length=20)
    order_description = models.TextField()
    organisation = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, null=True, blank=True)
    is_cancelled = models.BooleanField(default=False)
    products = models.ManyToManyField(ProductsAndStock, through='OrderProduct')
    creation_date = models.DateTimeField(default=timezone.now)  # Ensure this is timezone-aware

    def __str__(self):
        return self.order_name

    @property
    def total_order_price(self):
        """Sum of all line items' total_price."""
        return sum(op.total_price for op in self.orderproduct_set.all())

    @property
    def items_count(self):
        """Total number of line items (product rows)."""
        return self.orderproduct_set.count()


class OrderProduct(models.Model):
    order = models.ForeignKey(orders, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductsAndStock, on_delete=models.CASCADE)
    product_quantity = models.PositiveIntegerField()
    total_price = models.FloatField(default=0.0)  # New field

    def __str__(self):
        return f"{self.order.order_name} - {self.product.product_name}"
    
    def save(self, *args, **kwargs):
        self.total_price = self.product_quantity * self.product.product_price
        super().save(*args, **kwargs)
    
    def reduce_stock(self):
        """Reduce stock when order is confirmed"""
        if not self.order.is_cancelled:
            # Check if enough stock is available
            if self.product.product_quantity >= self.product_quantity:
                # Store previous quantity
                previous_quantity = self.product.product_quantity
                
                # Reduce stock (skip ProductsAndStock post_save stock movement to avoid duplicate)
                self.product.product_quantity -= self.product_quantity
                self.product._skip_stock_movement_signal = True
                self.product.save()
                
                # Create stock movement record
                StockMovement.objects.create(
                    product=self.product,
                    movement_type='OUT',
                    quantity_before=previous_quantity,
                    quantity_after=self.product.product_quantity,
                    quantity_change=-self.product_quantity,
                    reason=f'Sale - Order: {self.order.order_name}',
                    created_by=getattr(self.order, '_current_user', None)
                )
                
                return True
            else:
                # Not enough stock
                return False
        return True
    
    def restore_stock(self):
        """Restore stock when order is cancelled"""
        if self.order.is_cancelled:
            # Store previous quantity
            previous_quantity = self.product.product_quantity
            
            # Restore stock (skip ProductsAndStock post_save stock movement to avoid duplicate)
            self.product.product_quantity += self.product_quantity
            self.product._skip_stock_movement_signal = True
            self.product.save()
            
            # Create stock movement record
            StockMovement.objects.create(
                product=self.product,
                movement_type='IN',
                quantity_before=previous_quantity,
                quantity_after=self.product.product_quantity,
                quantity_change=self.product_quantity,
                reason=f'Order Cancellation - Order: {self.order.order_name}',
                created_by=getattr(self.order, '_current_user', None)
            )

# Signals for automatic stock management
@receiver(post_save, sender=OrderProduct)
def handle_order_product_created(sender, instance, created, **kwargs):
    """Handle stock reduction when order product is created"""
    if created and not instance.order.is_cancelled:
        # Automatically reduce stock when order product is created
        success = instance.reduce_stock()
        if not success:
            # If not enough stock, you might want to raise an exception
            # or handle this differently based on your business logic
            print(f"Insufficient stock for product {instance.product.product_name}")

@receiver(pre_delete, sender=OrderProduct)
def handle_order_product_deleted(sender, instance, **kwargs):
    """Handle stock restoration when order product is deleted"""
    if not instance.order.is_cancelled:
        # Restore stock when order product is deleted
        instance.restore_stock()

@receiver(post_save, sender=orders)
def handle_order_cancellation(sender, instance, **kwargs):
    """Handle stock restoration when order is cancelled"""
    if instance.is_cancelled:
        # Restore stock for all products in cancelled order
        for order_product in instance.orderproduct_set.all():
            order_product.restore_stock()


