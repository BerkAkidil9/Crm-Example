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
            'minimum_stock_level',
        ]
        widgets = {
            'product_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product Name'}),
            'product_description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Product Description', 'rows': 3}),
            'product_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'product_quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'minimum_stock_level': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0', 'help_text': 'Minimum stock level for alerts'}),
        }
    
    def clean_product_name(self):
        product_name = self.cleaned_data.get('product_name')
        organisation = self.instance.organisation if self.instance.pk else None
        
        # Eğer instance varsa (update), organisation'ı instance'dan al
        if not organisation and hasattr(self, 'user_organisation'):
            organisation = self.user_organisation
        
        if organisation:
            # Aynı organizasyon altında aynı isimde ürün var mı kontrol et
            existing_product = ProductsAndStock.objects.filter(
                product_name=product_name,
                organisation=organisation
            ).exclude(pk=self.instance.pk if self.instance.pk else None)
            
            if existing_product.exists():
                raise forms.ValidationError(
                    f"A product with the name '{product_name}' already exists in this organization."
                )
        
        return product_name

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
            'minimum_stock_level',
            'organisation',
        ]
        widgets = {
            'product_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product Name'}),
            'product_description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Product Description', 'rows': 3}),
            'product_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'product_quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'minimum_stock_level': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0', 'help_text': 'Minimum stock level for alerts'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        product_name = cleaned_data.get('product_name')
        organisation = cleaned_data.get('organisation')
        
        if product_name and organisation:
            # Aynı organizasyon altında aynı isimde ürün var mı kontrol et
            existing_product = ProductsAndStock.objects.filter(
                product_name=product_name,
                organisation=organisation
            ).exclude(pk=self.instance.pk if self.instance.pk else None)
            
            if existing_product.exists():
                raise forms.ValidationError(
                    f"A product with the name '{product_name}' already exists in this organization."
                )
        
        return cleaned_data
