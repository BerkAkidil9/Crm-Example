from django import forms
from django.utils import timezone
from datetime import timedelta


DATE_FILTER_CHOICES = [
    ('creation_date', 'By Creation Date'),
    ('order_day', 'By Order Date'),
]


class DateRangeForm(forms.Form):
    date_filter = forms.ChoiceField(
        choices=DATE_FILTER_CHOICES,
        initial='creation_date',
        widget=forms.RadioSelect(attrs={'class': 'mr-4'}),
        required=False
    )
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'text',
            'id': 'start_date',
            'placeholder': 'DD-MM-YYYY',
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500',
            'autocomplete': 'off'
        }),
        required=True
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'text',
            'id': 'end_date',
            'placeholder': 'DD-MM-YYYY',
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500',
            'autocomplete': 'off'
        }),
        required=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Default: first day of month to today (e.g. 1 Feb - 8 Feb)
        if not self.data and not self.initial:
            today = timezone.localdate()
            first = today.replace(day=1)
            self.initial = {'date_filter': 'creation_date', 'start_date': first, 'end_date': today}

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("End date must be after start date.")
        return cleaned_data
