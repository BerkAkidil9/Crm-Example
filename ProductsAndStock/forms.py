from django import forms
from django.contrib.auth import get_user_model
from .models import ProductsAndStock, Category, SubCategory
from leads.models import UserProfile

User = get_user_model()

class ProductAndStockModelForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=True,
        empty_label="Select Category *",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    subcategory = forms.ModelChoiceField(
        queryset=SubCategory.objects.none(),
        required=True,
        empty_label="Select Sub Category *",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = ProductsAndStock
        fields = [
            'product_name',
            'product_description',
            'product_price',
            'cost_price',
            'product_quantity',
            'minimum_stock_level',
            'category',
            'subcategory',
            'discount_percentage',
            'discount_amount',
            'discount_start_date',
            'discount_end_date',
        ]
        widgets = {
            'product_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product Name'}),
            'product_description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Product Description', 'rows': 3}),
            'product_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'cost_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'product_quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'minimum_stock_level': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0', 'help_text': 'Minimum stock level for alerts'}),
            'discount_percentage': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0', 'step': '0.01', 'max': '100'}),
            'discount_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'discount_start_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'discount_end_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # If we have a category selected, populate subcategories
        if 'category' in self.data:
            try:
                category_id = int(self.data.get('category'))
                self.fields['subcategory'].queryset = SubCategory.objects.filter(category_id=category_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.category:
            self.fields['subcategory'].queryset = self.instance.category.subcategories.all()
    
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
    
    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        subcategory = cleaned_data.get('subcategory')
        
        # Validate that subcategory belongs to the selected category
        if category and subcategory:
            if subcategory.category != category:
                raise forms.ValidationError(
                    f"Subcategory '{subcategory.name}' does not belong to category '{category.name}'"
                )
        
        return cleaned_data

class AdminProductAndStockModelForm(forms.ModelForm):
    organisation = forms.ModelChoiceField(
        queryset=UserProfile.objects.filter(
            user__is_organisor=True,
            user__is_superuser=False
        ),
        empty_label="Select Organisation",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=True,
        empty_label="Select Category *",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    subcategory = forms.ModelChoiceField(
        queryset=SubCategory.objects.none(),
        required=True,
        empty_label="Select Sub Category *",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = ProductsAndStock
        fields = [
            'product_name',
            'product_description',
            'product_price',
            'cost_price',
            'product_quantity',
            'minimum_stock_level',
            'category',
            'subcategory',
            'discount_percentage',
            'discount_amount',
            'discount_start_date',
            'discount_end_date',
            'organisation',
        ]
        widgets = {
            'product_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product Name'}),
            'product_description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Product Description', 'rows': 3}),
            'product_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'cost_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'product_quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'minimum_stock_level': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0', 'help_text': 'Minimum stock level for alerts'}),
            'discount_percentage': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0', 'step': '0.01', 'max': '100'}),
            'discount_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'discount_start_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'discount_end_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # If we have a category selected, populate subcategories
        if 'category' in self.data:
            try:
                category_id = int(self.data.get('category'))
                self.fields['subcategory'].queryset = SubCategory.objects.filter(category_id=category_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.category:
            self.fields['subcategory'].queryset = self.instance.category.subcategories.all()
    
    def clean(self):
        cleaned_data = super().clean()
        product_name = cleaned_data.get('product_name')
        organisation = cleaned_data.get('organisation')
        category = cleaned_data.get('category')
        subcategory = cleaned_data.get('subcategory')
        
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
        
        # Validate that subcategory belongs to the selected category
        if category and subcategory:
            if subcategory.category != category:
                raise forms.ValidationError(
                    f"Subcategory '{subcategory.name}' does not belong to category '{category.name}'"
                )
        
        return cleaned_data
