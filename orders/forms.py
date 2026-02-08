from django import forms
from django.utils import timezone
from .models import orders, OrderProduct
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
            if quantity > product.product_quantity:
                raise forms.ValidationError(f"Only {product.product_quantity} items available in stock.")
        return quantity

OrderProductFormSet = inlineformset_factory(
    orders, OrderProduct, 
    form=OrderForm, 
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

    def clean_order_day(self):
        order_day = self.cleaned_data.get('order_day')
        if order_day and timezone.is_naive(order_day):
            order_day = timezone.make_aware(order_day, timezone.get_current_timezone())
        return order_day
