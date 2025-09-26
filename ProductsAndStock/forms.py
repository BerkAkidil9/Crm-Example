from django import forms
from django.contrib.auth import get_user_model
from .models import ProductsAndStock

User = get_user_model()

class ProductAndStockModelForm(forms.ModelForm):
    class Meta:
        model = ProductsAndStock
        fields = [
            'product_name',
            'product_description',
            'product_price',
            'product_quantity',

        ]
