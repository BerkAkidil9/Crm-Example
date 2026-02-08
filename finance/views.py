from django.shortcuts import render
from django.views import View
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Count, F, FloatField, ExpressionWrapper
from datetime import datetime, timedelta

from .models import OrderFinanceReport
from .forms import DateRangeForm
from orders.models import orders, OrderProduct
from leads.models import Agent, UserProfile


def get_organisation_for_user(user):
    """Return the UserProfile (organisation) for filtering. Matches orders logic."""
    if user.is_superuser:
        return None
    if getattr(user, "is_agent", False):
        try:
            return Agent.objects.get(user=user).organisation
        except Agent.DoesNotExist:
            return getattr(user, "userprofile", None)
    return getattr(user, "userprofile", None)


class FinancialReportView(LoginRequiredMixin, View):
    template_name = 'finance/financial_report.html'

    def get_queryset(self, start_datetime, end_datetime, date_filter='creation_date'):
        """Base queryset filtered by date range and organisation.
        date_filter: 'creation_date' = when order was entered in CRM
                     'order_day' = when order/sale date is (e.g. expected payment date)
        """
        date_field = 'order__order_day' if date_filter == 'order_day' else 'order__creation_date'
        filter_kwargs = {
            date_field + '__range': [start_datetime, end_datetime],
            'order__is_cancelled': False,
        }
        qs = OrderFinanceReport.objects.filter(**filter_kwargs).select_related(
            'order', 'order__lead', 'order__organisation', 'order__organisation__user'
        ).prefetch_related('order__orderproduct_set__product')

        user = self.request.user
        org_id = self.request.GET.get('organisation') or self.request.POST.get('organisation')
        agent_id = self.request.GET.get('agent') or self.request.POST.get('agent')

        if user.is_superuser:
            if org_id:
                qs = qs.filter(order__organisation_id=org_id)
            if agent_id:
                qs = qs.filter(order__lead__agent_id=agent_id)
        elif user.is_organisor:
            org = get_organisation_for_user(user)
            if org:
                qs = qs.filter(order__organisation=org)
            if agent_id:
                qs = qs.filter(order__lead__agent_id=agent_id)
        elif user.is_agent:
            try:
                agent = Agent.objects.get(user=user)
                qs = qs.filter(order__lead__agent=agent)
            except Agent.DoesNotExist:
                qs = qs.none()

        order_by = '-order__order_day' if date_filter == 'order_day' else '-order__creation_date'
        return qs.order_by(order_by)

    def get_date_filter(self):
        """Get selected date filter from request (creation_date or order_day)."""
        val = self.request.GET.get('date_filter') or self.request.POST.get('date_filter') or 'creation_date'
        return val if val in ('creation_date', 'order_day') else 'creation_date'

    def get_context_filters(self):
        """Context for organisation and agent filters."""
        user = self.request.user
        selected_org = self.request.GET.get('organisation') or self.request.POST.get('organisation') or ''
        selected_agent = self.request.GET.get('agent') or self.request.POST.get('agent') or ''
        selected_date_filter = self.get_date_filter()

        ctx = {
            'selected_organisation_id': selected_org,
            'selected_agent_id': selected_agent,
            'selected_date_filter': selected_date_filter,
            'show_organisation_filter': False,
            'organisations': [],
            'agents': [],
        }

        if user.is_superuser:
            ctx['show_organisation_filter'] = True
            org_qs = UserProfile.objects.filter(user__is_organisor=True).select_related('user').order_by('user__username')
            profile = getattr(user, 'userprofile', None)
            if profile:
                org_qs = org_qs.exclude(pk=profile.pk)
            ctx['organisations'] = org_qs
            if selected_org:
                ctx['agents'] = Agent.objects.filter(organisation_id=selected_org).select_related('user').order_by('user__username')
        elif user.is_organisor:
            org = get_organisation_for_user(user)
            if org:
                ctx['agents'] = Agent.objects.filter(organisation=org).select_related('user').order_by('user__username')

        return ctx

    def get(self, request, *args, **kwargs):
        form = DateRangeForm()
        if not form.data:
            form.initial['date_filter'] = self.get_date_filter()
        # Show default (current month) report on first load
        if form.initial.get('start_date') and form.initial.get('end_date'):
            start_date = form.initial['start_date']
            end_date = form.initial['end_date']
            date_filter = self.get_date_filter()
            start_datetime = timezone.make_aware(datetime.combine(start_date, datetime.min.time()))
            end_datetime = timezone.make_aware(datetime.combine(end_date, datetime.max.time()))
            reports = self.get_queryset(start_datetime, end_datetime, date_filter)
            agg = reports.aggregate(total=Sum('earned_amount'), count=Count('id'))
            total_earned = agg['total'] or 0
            order_count = agg['count'] or 0
            average_per_order = round(total_earned / order_count, 2) if order_count else None
            order_ids = list(reports.values_list('order_id', flat=True))
            total_cost = self._get_total_cost(order_ids)
            total_profit = round(total_earned - total_cost, 2)
        else:
            total_earned = None
            total_cost = None
            total_profit = None
            reports = []
            order_count = 0
            average_per_order = None

        report_rows = self._get_report_rows(reports) if reports else []
        context = {
            'form': form,
            'total_earned': total_earned,
            'total_cost': total_cost,
            'total_profit': total_profit,
            'reports': reports,
            'report_rows': report_rows,
            'order_count': order_count,
            'average_per_order': average_per_order,
        }
        context.update(self.get_context_filters())
        return render(request, self.template_name, context)

    def _get_total_cost(self, order_ids):
        """Calculate total cost from OrderProduct for given order IDs."""
        if not order_ids:
            return 0
        result = OrderProduct.objects.filter(order_id__in=order_ids).annotate(
            line_cost=ExpressionWrapper(F('product_quantity') * F('product__cost_price'), output_field=FloatField())
        ).aggregate(total=Sum('line_cost'))
        return round(result['total'] or 0, 2)

    def _get_report_rows(self, reports):
        """Return list of dicts with report, cost, profit for each order."""
        rows = []
        for r in reports:
            cost = sum(op.product_quantity * op.product.cost_price for op in r.order.orderproduct_set.all())
            profit = round(r.earned_amount - cost, 2)
            rows.append({'report': r, 'cost': round(cost, 2), 'profit': profit})
        return rows

    def post(self, request, *args, **kwargs):
        form = DateRangeForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            date_filter = form.cleaned_data.get('date_filter', 'creation_date')

            start_datetime = timezone.make_aware(datetime.combine(start_date, datetime.min.time()))
            end_datetime = timezone.make_aware(datetime.combine(end_date, datetime.max.time()))

            reports = self.get_queryset(start_datetime, end_datetime, date_filter)

            agg = reports.aggregate(total=Sum('earned_amount'), count=Count('id'))
            total_earned = agg['total'] or 0
            order_count = agg['count'] or 0
            average_per_order = round(total_earned / order_count, 2) if order_count else None
            order_ids = list(reports.values_list('order_id', flat=True))
            total_cost = self._get_total_cost(order_ids)
            total_profit = round(total_earned - total_cost, 2)

            report_rows = self._get_report_rows(reports) if reports else []
            context = {
                'form': form,
                'reports': reports,
                'report_rows': report_rows,
                'total_earned': total_earned,
                'total_cost': total_cost,
                'total_profit': total_profit,
                'order_count': order_count,
                'average_per_order': average_per_order,
                'start_date': start_date,
                'end_date': end_date,
                'date_filter': date_filter,
            }
            context.update(self.get_context_filters())
            return render(request, self.template_name, context)

        context = {'form': form, 'total_earned': None, 'total_cost': None, 'total_profit': None, 'reports': [], 'report_rows': [], 'order_count': 0, 'average_per_order': None}
        context.update(self.get_context_filters())
        return render(request, self.template_name, context)
