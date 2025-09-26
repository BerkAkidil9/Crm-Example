from django import forms

class DateRangeForm(forms.Form):
    start_date = forms.DateField(widget=forms.SelectDateWidget(years=range(2000, 2101)))
    end_date = forms.DateField(widget=forms.SelectDateWidget(years=range(2000, 2101)))

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("End date must be after start date.")
