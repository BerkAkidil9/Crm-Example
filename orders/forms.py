from datetime import timedelta
from collections import defaultdict

from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import transaction
from django.forms import BaseInlineFormSet
from .models import orders, OrderProduct, lock_products, change_stock, sync_finance
from leads.models import Lead
from ProductsAndStock.models import ProductsAndStock
from django.forms import inlineformset_factory

class OrderForm(forms.ModelForm):
    product_quantity = forms.IntegerField(min_value=1, label='Product Quantity')
    product = forms.ModelChoiceField(queryset=ProductsAndStock.objects.all(), required=False)

    class Meta:
        model = OrderProduct
        fields = ['id', 'product', 'product_quantity']  # Ensure 'id' is included

    def clean_product_quantity(self):
        product = self.cleaned_data.get('product')
        quantity = self.cleaned_data.get('product_quantity')
        if product and quantity:
            if getattr(self, 'aggregate_stock_validation', False):
                return quantity
            if self.instance.pk and self.instance.order.is_cancelled:
                return quantity
            reserved = 0
            if self.instance.pk:
                previous = OrderProduct.objects.get(pk=self.instance.pk)
                if previous.product_id == product.pk:
                    reserved = previous.product_quantity
            if quantity > product.product_quantity + reserved:
                raise forms.ValidationError(f"Only {product.product_quantity} items available in stock.")
        return quantity

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('product_quantity') and not cleaned.get('product'):
            self.add_error('product', 'This field is required.')
        return cleaned


class BaseOrderProductFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        organisation = kwargs.pop('organisation', None)
        super().__init__(*args, **kwargs)
        if organisation is None and self.instance.organisation_id:
            organisation = self.instance.organisation
        # Creation views restrict product choices after organisation selection;
        # existing orders can also derive their scope directly from the instance.
        for form in self.forms:
            form.aggregate_stock_validation = True
            if organisation is not None:
                form.fields['product'].queryset = ProductsAndStock.objects.filter(organisation=organisation)

    def requested_quantities(self):
        quantities = defaultdict(int)
        existing_ids = set(self.get_queryset().values_list('pk', flat=True))
        seen_ids = set()
        for form in self.forms:
            item = form.cleaned_data.get('id')
            if item:
                if item.pk not in existing_ids or item.pk in seen_ids:
                    raise ValidationError('Invalid or duplicate order item.')
                seen_ids.add(item.pk)
            if form.cleaned_data.get('DELETE'):
                continue
            product = form.cleaned_data.get('product')
            quantity = form.cleaned_data.get('product_quantity')
            if product and quantity:
                quantities[product.pk] += quantity
        if self.is_bound and (seen_ids != existing_ids or self.initial_form_count() != len(existing_ids)):
            raise ValidationError('All existing order items must be submitted.')
        return quantities

    def clean(self):
        super().clean()
        if any(form.errors for form in self.forms if not self._should_delete_form(form)):
            return
        quantities = self.requested_quantities()
        if not quantities:
            raise ValidationError('Please add at least one product with quantity.')
        if self.instance.is_cancelled:
            return
        reserved = defaultdict(int)
        if self.instance.pk:
            for item in OrderProduct.objects.filter(order=self.instance):
                reserved[item.product_id] += item.product_quantity
        for product in ProductsAndStock.objects.filter(pk__in=quantities):
            available = product.product_quantity + reserved[product.pk]
            if quantities[product.pk] > available:
                raise ValidationError(
                    f'Only {available} items available in stock for {product.product_name}; '
                    f'{quantities[product.pk]} requested across all rows.'
                )

    def save(self, commit=True):
        if not commit:
            return super().save(commit=False)
        with transaction.atomic():
            order = orders.objects.select_for_update().get(pk=self.instance.pk)
            order._current_user = getattr(self.instance, '_current_user', None)
            self.instance.is_cancelled = order.is_cancelled
            previous = defaultdict(int)
            for item in OrderProduct.objects.filter(order=order):
                previous[item.product_id] += item.product_quantity
            requested = self.requested_quantities()
            products = lock_products(set(previous) | set(requested))
            # Repeat aggregate validation under the stock locks: another order
            # may have reserved items after the form was first validated.
            self.clean()
            if not order.is_cancelled:
                changes = {pk: previous[pk] - requested[pk] for pk in products}
                change_stock(products, changes, order, f'Order Reservation - Order: {order.order_name}')
            instances = super().save(commit=False)
            for item in self.deleted_objects:
                item._stock_already_reconciled = True
                try:
                    item.delete()
                finally:
                    del item._stock_already_reconciled
            for item in instances:
                item.order = self.instance
                item._stock_already_reconciled = True
                try:
                    item.save()
                finally:
                    del item._stock_already_reconciled
            self.save_m2m()
            sync_finance(order.pk)
            return instances


OrderProductFormSet = inlineformset_factory(
    orders, OrderProduct, 
    form=OrderForm, 
    formset=BaseOrderProductFormSet,
    fields=['id', 'product', 'product_quantity'],  # Ensure 'id' is included
    extra=1,  # Start with one form, more can be added dynamically
    can_delete=True  # Allow deletion of order products
)

class OrderModelForm(forms.ModelForm):
    class Meta:
        model = orders
        fields = [ 
            'order_day',
            'order_name',
            'order_description',
            'lead',
        ]
        widgets = {
            'order_day': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'},
                format='%Y-%m-%dT%H:%M',
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['order_day'].input_formats = ['%Y-%m-%dT%H:%M', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%d']
        now = timezone.now()
        self.fields['order_day'].widget.attrs['min'] = now.strftime('%Y-%m-%dT%H:%M')

    def clean_order_day(self):
        order_day = self.cleaned_data.get('order_day')
        if order_day:
            if timezone.is_naive(order_day):
                order_day = timezone.make_aware(order_day, timezone.get_current_timezone())
            # Allow up to 1 minute in the past to avoid validation failure due to submit delay
            if order_day < timezone.now() - timedelta(minutes=1):
                raise forms.ValidationError('Order day cannot be in the past. Please select current time or a future date.')
        return order_day
