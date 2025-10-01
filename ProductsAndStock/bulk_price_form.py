from django import forms
from .models import Category, SubCategory

class BulkPriceUpdateForm(forms.Form):
    UPDATE_TYPE_CHOICES = [
        ('PERCENTAGE_INCREASE', 'Percentage Increase'),
        ('PERCENTAGE_DECREASE', 'Percentage Decrease'),
        ('FIXED_AMOUNT_INCREASE', 'Fixed Amount Increase'),
        ('FIXED_AMOUNT_DECREASE', 'Fixed Amount Decrease'),
        ('SET_PRICE', 'Set New Price'),
    ]
    
    CATEGORY_CHOICES = [
        ('ALL', 'All Products'),
        ('CATEGORY', 'By Category'),
        ('SUBCATEGORY', 'By Sub Category'),
    ]
    
    update_type = forms.ChoiceField(
        choices=UPDATE_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    category_filter = forms.ChoiceField(
        choices=CATEGORY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="Select Category",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    subcategory = forms.ModelChoiceField(
        queryset=SubCategory.objects.none(),
        required=False,
        empty_label="Select Sub Category",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    percentage_increase = forms.FloatField(
        required=False,
        min_value=0,
        max_value=1000,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0', 'step': '0.01'})
    )
    
    percentage_decrease = forms.FloatField(
        required=False,
        min_value=0,
        max_value=100,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0', 'step': '0.01'})
    )
    
    fixed_amount_increase = forms.FloatField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'})
    )
    
    fixed_amount_decrease = forms.FloatField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'})
    )
    
    new_price = forms.FloatField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'})
    )
    
    reason = forms.CharField(
        required=False,
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Reason for price update'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        update_type = cleaned_data.get('update_type')
        percentage_increase = cleaned_data.get('percentage_increase')
        percentage_decrease = cleaned_data.get('percentage_decrease')
        fixed_amount_increase = cleaned_data.get('fixed_amount_increase')
        fixed_amount_decrease = cleaned_data.get('fixed_amount_decrease')
        new_price = cleaned_data.get('new_price')
        
        if update_type == 'PERCENTAGE_INCREASE' and not percentage_increase:
            raise forms.ValidationError("Percentage increase is required for percentage increase update.")
        
        if update_type == 'PERCENTAGE_DECREASE' and not percentage_decrease:
            raise forms.ValidationError("Percentage decrease is required for percentage decrease update.")
        
        if update_type == 'FIXED_AMOUNT_INCREASE' and not fixed_amount_increase:
            raise forms.ValidationError("Fixed amount increase is required for fixed amount increase update.")
        
        if update_type == 'FIXED_AMOUNT_DECREASE' and not fixed_amount_decrease:
            raise forms.ValidationError("Fixed amount decrease is required for fixed amount decrease update.")
        
        if update_type == 'SET_PRICE' and not new_price:
            raise forms.ValidationError("New price is required for set price update.")
        
        return cleaned_data
