# finance/urls.py
from django.urls import path
from .views import FinancialReportView

app_name = 'finance'

urlpatterns = [
    path('', FinancialReportView.as_view(), name='financial_report'),
]
