from django import forms
from django.contrib.auth import get_user_model
from .models import ProductsAndStock
from leads.models import UserProfile

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

class AdminProductAndStockModelForm(forms.ModelForm):
    organisation = forms.ModelChoiceField(
        queryset=UserProfile.objects.filter(
            user__is_organisor=True,
            user__is_superuser=False
        ),
        empty_label="Select Organisation",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = ProductsAndStock
        fields = [
            'product_name',
            'product_description',
            'product_price',
            'product_quantity',
            'organisation',
        ]
