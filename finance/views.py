from django.shortcuts import render
from django.views import View
from django.utils import timezone
from .models import OrderFinanceReport
from .forms import DateRangeForm
from django.db.models import Sum
from datetime import datetime

class FinancialReportView(View):
    template_name = 'finance/financial_report.html'

    def get(self, request, *args, **kwargs):
        form = DateRangeForm()
        return render(request, self.template_name, {
            'form': form,
            'total_earned': None,
            'reports': []
        })

    def post(self, request, *args, **kwargs):
        form = DateRangeForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']

            # Ensure start_date and end_date are datetime objects with time set to midnight
            start_datetime = timezone.make_aware(datetime.combine(start_date, datetime.min.time()))
            end_datetime = timezone.make_aware(datetime.combine(end_date, datetime.max.time()))

            # Filtering by order creation date and order day
            reports = OrderFinanceReport.objects.filter(
                order__creation_date__range=[start_datetime, end_datetime]
            ).select_related('order')

            total_earned = reports.aggregate(total=Sum('earned_amount'))['total'] or 0

            return render(request, self.template_name, {
                'form': form,
                'reports': reports,
                'total_earned': total_earned
            })
        return self.get(request, *args, **kwargs)
