"""
Finance Forms Test File
This file tests all forms in the Finance module.
"""

import os
import sys
import django
from django.test import TestCase
from django.core.exceptions import ValidationError
from datetime import date, timedelta

# Load Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djcrm.settings')
django.setup()

from finance.forms import DateRangeForm


class TestDateRangeForm(TestCase):
    """DateRangeForm tests"""
    
    def test_date_range_form_valid_data(self):
        """DateRangeForm valid data test"""
        today = date.today()
        tomorrow = today + timedelta(days=1)
        
        form_data = {
            'start_date': today,
            'end_date': tomorrow
        }
        
        form = DateRangeForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['start_date'], today)
        self.assertEqual(form.cleaned_data['end_date'], tomorrow)
    
    def test_date_range_form_same_dates(self):
        """DateRangeForm same dates test"""
        today = date.today()
        
        form_data = {
            'start_date': today,
            'end_date': today
        }
        
        form = DateRangeForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['start_date'], today)
        self.assertEqual(form.cleaned_data['end_date'], today)
    
    def test_date_range_form_end_date_before_start_date(self):
        """DateRangeForm end_date before start_date test"""
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        form_data = {
            'start_date': today,
            'end_date': yesterday
        }
        
        form = DateRangeForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('End date must be after start date.', form.errors['__all__'])
    
    def test_date_range_form_empty_data(self):
        """DateRangeForm empty data test"""
        form_data = {}
        
        form = DateRangeForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('start_date', form.errors)
        self.assertIn('end_date', form.errors)
    
    def test_date_range_form_missing_start_date(self):
        """DateRangeForm missing start_date test"""
        today = date.today()
        
        form_data = {
            'end_date': today
        }
        
        form = DateRangeForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('start_date', form.errors)
        self.assertNotIn('end_date', form.errors)
    
    def test_date_range_form_missing_end_date(self):
        """DateRangeForm missing end_date test"""
        today = date.today()
        
        form_data = {
            'start_date': today
        }
        
        form = DateRangeForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertNotIn('start_date', form.errors)
        self.assertIn('end_date', form.errors)
    
    def test_date_range_form_invalid_date_format(self):
        """DateRangeForm invalid date format test"""
        form_data = {
            'start_date': 'invalid_date',
            'end_date': 'invalid_date'
        }
        
        form = DateRangeForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('start_date', form.errors)
        self.assertIn('end_date', form.errors)
    
    def test_date_range_form_future_dates(self):
        """DateRangeForm future dates test"""
        future_date1 = date.today() + timedelta(days=10)
        future_date2 = date.today() + timedelta(days=20)
        
        form_data = {
            'start_date': future_date1,
            'end_date': future_date2
        }
        
        form = DateRangeForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['start_date'], future_date1)
        self.assertEqual(form.cleaned_data['end_date'], future_date2)
    
    def test_date_range_form_past_dates(self):
        """DateRangeForm past dates test"""
        past_date1 = date.today() - timedelta(days=30)
        past_date2 = date.today() - timedelta(days=10)
        
        form_data = {
            'start_date': past_date1,
            'end_date': past_date2
        }
        
        form = DateRangeForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['start_date'], past_date1)
        self.assertEqual(form.cleaned_data['end_date'], past_date2)
    
    def test_date_range_form_widget_years_range(self):
        """DateRangeForm widget years range test"""
        form = DateRangeForm()
        
        # Check widgets' years range
        start_date_widget = form.fields['start_date'].widget
        end_date_widget = form.fields['end_date'].widget
        
        # Compare with range object
        self.assertEqual(start_date_widget.years, range(2000, 2101))
        self.assertEqual(end_date_widget.years, range(2000, 2101))
    
    def test_date_range_form_clean_method(self):
        """DateRangeForm clean method test"""
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        form_data = {
            'start_date': today,
            'end_date': yesterday
        }
        
        form = DateRangeForm(data=form_data)
        
        # Form'u validate et
        self.assertFalse(form.is_valid())
        self.assertIn('End date must be after start date.', form.errors['__all__'])
    
    def test_date_range_form_clean_method_valid(self):
        """DateRangeForm clean method valid test"""
        today = date.today()
        tomorrow = today + timedelta(days=1)
        
        form_data = {
            'start_date': today,
            'end_date': tomorrow
        }
        
        form = DateRangeForm(data=form_data)
        
        # Form should be valid
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['start_date'], today)
        self.assertEqual(form.cleaned_data['end_date'], tomorrow)
    
    def test_date_range_form_clean_method_same_dates(self):
        """DateRangeForm clean method same dates test"""
        today = date.today()
        
        form_data = {
            'start_date': today,
            'end_date': today
        }
        
        form = DateRangeForm(data=form_data)
        
        # Form should be valid (same dates are valid)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['start_date'], today)
        self.assertEqual(form.cleaned_data['end_date'], today)
    
    def test_date_range_form_field_types(self):
        """DateRangeForm field types test"""
        form = DateRangeForm()
        
        # Check field types
        self.assertEqual(form.fields['start_date'].__class__.__name__, 'DateField')
        self.assertEqual(form.fields['end_date'].__class__.__name__, 'DateField')
    
    def test_date_range_form_field_required(self):
        """DateRangeForm field required test"""
        form = DateRangeForm()
        
        # Check whether fields are required
        self.assertTrue(form.fields['start_date'].required)
        self.assertTrue(form.fields['end_date'].required)
    
    def test_date_range_form_field_labels(self):
        """DateRangeForm field labels test"""
        form = DateRangeForm()
        
        # Check field labels (Django creates labels automatically)
        # If label is None, Django creates it from field name
        self.assertIsNone(form.fields['start_date'].label)  # Should be None
        self.assertIsNone(form.fields['end_date'].label)    # Should be None
    
    def test_date_range_form_initial_data(self):
        """DateRangeForm initial data test"""
        today = date.today()
        tomorrow = today + timedelta(days=1)
        
        initial_data = {
            'start_date': today,
            'end_date': tomorrow
        }
        
        form = DateRangeForm(initial=initial_data)
        
        # Initial data should be set correctly
        self.assertEqual(form.initial['start_date'], today)
        self.assertEqual(form.initial['end_date'], tomorrow)
    
    def test_date_range_form_bound_vs_unbound(self):
        """DateRangeForm bound vs unbound test"""
        # Unbound form
        unbound_form = DateRangeForm()
        self.assertFalse(unbound_form.is_bound)
        
        # Bound form
        today = date.today()
        tomorrow = today + timedelta(days=1)
        
        bound_form = DateRangeForm(data={
            'start_date': today,
            'end_date': tomorrow
        })
        self.assertTrue(bound_form.is_bound)
    
    def test_date_range_form_clean_data_access(self):
        """DateRangeForm clean_data access test"""
        today = date.today()
        tomorrow = today + timedelta(days=1)
        
        form_data = {
            'start_date': today,
            'end_date': tomorrow
        }
        
        form = DateRangeForm(data=form_data)
        
        # Access cleaned_data before form is valid
        with self.assertRaises(AttributeError):
            _ = form.cleaned_data
        
        # Form'u validate et
        self.assertTrue(form.is_valid())
        
        # Now access to cleaned_data should be available
        self.assertEqual(form.cleaned_data['start_date'], today)
        self.assertEqual(form.cleaned_data['end_date'], tomorrow)
    
    def test_date_range_form_error_messages(self):
        """DateRangeForm error messages test"""
        form_data = {
            'start_date': 'invalid',
            'end_date': 'invalid'
        }
        
        form = DateRangeForm(data=form_data)
        self.assertFalse(form.is_valid())
        
        # Check error messages
        self.assertIn('start_date', form.errors)
        self.assertIn('end_date', form.errors)
        
        # Error messages should be a list
        self.assertIsInstance(form.errors['start_date'], list)
        self.assertIsInstance(form.errors['end_date'], list)
    
    def test_date_range_form_validation_error_format(self):
        """DateRangeForm validation error format test"""
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        form_data = {
            'start_date': today,
            'end_date': yesterday
        }
        
        form = DateRangeForm(data=form_data)
        self.assertFalse(form.is_valid())
        
        # Check __all__ error
        self.assertIn('__all__', form.errors)
        self.assertIn('End date must be after start date.', form.errors['__all__'])


class TestDateRangeFormEdgeCases(TestCase):
    """DateRangeForm edge cases tests"""
    
    def test_date_range_form_extreme_date_range(self):
        """DateRangeForm extreme date range test"""
        start_date = date(2000, 1, 1)
        end_date = date(2099, 12, 31)
        
        form_data = {
            'start_date': start_date,
            'end_date': end_date
        }
        
        form = DateRangeForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['start_date'], start_date)
        self.assertEqual(form.cleaned_data['end_date'], end_date)
    
    def test_date_range_form_leap_year_dates(self):
        """DateRangeForm leap year dates test"""
        leap_year_start = date(2024, 2, 29)  # 2024 is a leap year
        leap_year_end = date(2024, 3, 1)
        
        form_data = {
            'start_date': leap_year_start,
            'end_date': leap_year_end
        }
        
        form = DateRangeForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['start_date'], leap_year_start)
        self.assertEqual(form.cleaned_data['end_date'], leap_year_end)
    
    def test_date_range_form_year_boundary(self):
        """DateRangeForm year boundary test"""
        year_end = date(2023, 12, 31)
        year_start = date(2024, 1, 1)
        
        form_data = {
            'start_date': year_end,
            'end_date': year_start
        }
        
        form = DateRangeForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['start_date'], year_end)
        self.assertEqual(form.cleaned_data['end_date'], year_start)
    
    def test_date_range_form_none_values(self):
        """DateRangeForm None values test"""
        form_data = {
            'start_date': None,
            'end_date': None
        }
        
        form = DateRangeForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('start_date', form.errors)
        self.assertIn('end_date', form.errors)
    
    def test_date_range_form_empty_strings(self):
        """DateRangeForm empty strings test"""
        form_data = {
            'start_date': '',
            'end_date': ''
        }
        
        form = DateRangeForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('start_date', form.errors)
        self.assertIn('end_date', form.errors)


if __name__ == "__main__":
    print("Starting Finance Forms Tests...")
    print("=" * 60)
    
    # Run tests
    import unittest
    unittest.main()
