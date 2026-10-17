from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP

from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import Sum
from django.db.models.signals import pre_delete, post_delete
from django.dispatch import receiver
from django.utils import timezone

from leads.models import UserProfile, Lead
from ProductsAndStock.models import ProductsAndStock, StockMovement


def money(value):
    return float(Decimal(str(value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))


def lock_products(product_ids):
    product_ids = set(product_ids)
    products = {p.pk: p for p in ProductsAndStock.objects.select_for_update()
                .filter(pk__in=product_ids).order_by('pk')}
    if products.keys() != product_ids:
        raise ValidationError('A selected product is no longer available. Please reload the order.')
    return products


def change_stock(products, changes, order, reason):
    """Apply reservation deltas to locked, current product rows."""
    for product_id, change in changes.items():
        if not change:
            continue
        product = products[product_id]
        if product.organisation_id != order.organisation_id:
            raise ValidationError('Products must belong to the order organisation.')
        if product.product_quantity + change < 0:
            raise ValidationError(f'Only {product.product_quantity} items available in stock for {product.product_name}.')
    for product_id, change in changes.items():
        if not change:
            continue
        product = products[product_id]
        before = product.product_quantity
        product.product_quantity += change
        product._skip_stock_movement_signal = True
        product.save(update_fields=['product_quantity'])
        StockMovement.objects.create(
            product=product, movement_type='IN' if change > 0 else 'OUT',
            quantity_before=before, quantity_after=product.product_quantity,
            quantity_change=change, reason=reason,
            created_by=getattr(order, '_current_user', None),
        )


def sync_finance(order_id):
    from finance.models import OrderFinanceReport
    total = OrderProduct.objects.filter(order_id=order_id).aggregate(total=Sum('total_price'))['total'] or 0
    # Creation of the report belongs to the order creation workflow.
    OrderFinanceReport.objects.filter(order_id=order_id).update(earned_amount=money(total))


class orders(models.Model):
    order_day = models.DateTimeField()
    order_name = models.CharField(max_length=20)
    order_description = models.TextField()
    organisation = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, null=True, blank=True)
    is_cancelled = models.BooleanField(default=False)
    products = models.ManyToManyField(ProductsAndStock, through='OrderProduct')
    creation_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.order_name

    @property
    def total_order_price(self):
        return money(sum(op.total_price for op in self.orderproduct_set.all()))

    @property
    def items_count(self):
        return self.orderproduct_set.count()

    def save(self, *args, **kwargs):
        with transaction.atomic():
            previous = type(self).objects.select_for_update().filter(pk=self.pk).first() if self.pk else None
            if self.lead_id and self.lead.organisation_id != self.organisation_id:
                raise ValidationError('The lead must belong to the order organisation.')
            if previous and previous.organisation_id != self.organisation_id:
                raise ValidationError('The organisation of an existing order cannot be changed.')
            super().save(*args, **kwargs)
            fields = kwargs.get('update_fields')
            if previous and (fields is None or 'is_cancelled' in fields) and previous.is_cancelled != self.is_cancelled:
                quantities = defaultdict(int)
                for item in self.orderproduct_set.all():
                    quantities[item.product_id] += item.product_quantity
                products = lock_products(quantities)
                sign = 1 if self.is_cancelled else -1
                change_stock(products, {pk: sign * qty for pk, qty in quantities.items()}, self,
                             f'Order Cancellation - Order: {self.order_name}' if self.is_cancelled
                             else f'Order Reactivation - Order: {self.order_name}')


class OrderProduct(models.Model):
    order = models.ForeignKey(orders, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductsAndStock, on_delete=models.CASCADE)
    product_quantity = models.PositiveIntegerField()
    unit_price = models.FloatField(editable=False)
    unit_cost = models.FloatField(editable=False, null=True)
    total_price = models.FloatField(default=0.0)

    def __str__(self):
        return f'{self.order.order_name} - {self.product.product_name}'

    def save(self, *args, **kwargs):
        with transaction.atomic():
            order = orders.objects.select_for_update().get(pk=self.order_id)
            order._current_user = getattr(self.order, '_current_user', None)
            previous = type(self).objects.filter(pk=self.pk).first() if self.pk else None
            if previous and previous.order_id != self.order_id:
                raise ValidationError('An order item cannot be moved to another order.')
            if self.product_quantity is None or self.product_quantity < 1:
                raise ValidationError('Product quantity must be at least 1.')
            product_ids = {self.product_id}
            if previous:
                product_ids.add(previous.product_id)
            products = lock_products(product_ids)
            product = products[self.product_id]
            if product.organisation_id != order.organisation_id:
                raise ValidationError('Products must belong to the order organisation.')
            if previous and previous.product_id == self.product_id:
                self.unit_price = previous.unit_price if previous.unit_price is not None else money(previous.total_price / previous.product_quantity)
                self.unit_cost = previous.unit_cost
            else:
                self.unit_price = money(product.discounted_price)
                self.unit_cost = money(product.cost_price)
            self.total_price = money(Decimal(str(self.unit_price)) * self.product_quantity)
            managed = getattr(self, '_stock_already_reconciled', False)
            if not managed and not order.is_cancelled:
                changes = defaultdict(int)
                if previous:
                    changes[previous.product_id] += previous.product_quantity
                changes[self.product_id] -= self.product_quantity
                change_stock(products, changes, order,
                             f'Order Update - Order: {order.order_name}' if previous
                             else f'Sale - Order: {order.order_name}')
            if kwargs.get('update_fields') is not None:
                kwargs['update_fields'] = set(kwargs['update_fields']) | {'unit_price', 'unit_cost', 'total_price'}
            super().save(*args, **kwargs)
            if not managed:
                sync_finance(self.order_id)


@receiver(pre_delete, sender=OrderProduct)
def restore_deleted_item_stock(sender, instance, origin=None, **kwargs):
    if getattr(origin, '_stock_already_reconciled', False):
        return
    origin_model = getattr(origin, 'model', type(origin))
    # These cascades also remove the products; do not create new movements
    # referencing a product already scheduled for deletion by the collector.
    if getattr(getattr(origin_model, '_meta', None), 'label_lower', '') in {
        'productsandstock.productsandstock', 'productsandstock.category',
        'productsandstock.subcategory', 'leads.user', 'leads.userprofile',
    }:
        return
    with transaction.atomic():
        order = orders.objects.select_for_update().get(pk=instance.order_id)
        current = OrderProduct.objects.filter(pk=instance.pk).first()
        if current and not order.is_cancelled:
            products = lock_products([current.product_id])
            change_stock(products, {current.product_id: current.product_quantity}, order,
                         f'Order Item Deletion - Order: {order.order_name}')


@receiver(post_delete, sender=OrderProduct)
def update_deleted_item_finance(sender, instance, origin=None, **kwargs):
    if not getattr(origin, '_stock_already_reconciled', False):
        sync_finance(instance.order_id)
