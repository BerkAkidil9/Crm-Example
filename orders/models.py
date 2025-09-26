from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from leads.models import User, UserProfile, Lead
from ProductsAndStock.models import ProductsAndStock
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


