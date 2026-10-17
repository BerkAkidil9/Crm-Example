from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic, View
from django.urls import reverse_lazy, reverse
from .models import orders, OrderProduct
from leads.models import Lead, Agent
from leads.models import UserProfile
from activity_log.models import log_activity, ACTION_ORDER_CREATED, ACTION_ORDER_UPDATED, ACTION_ORDER_CANCELLED
from .forms import OrderModelForm, OrderForm, OrderProductFormSet
from ProductsAndStock.models import ProductsAndStock, Category, SubCategory
from django.http import HttpResponseRedirect
from django.forms import inlineformset_factory
from django.db import transaction
from django.core.exceptions import ValidationError
from django.contrib import messages
from finance.models import OrderFinanceReport
from django.utils import timezone
from tasks.models import Notification


def valid_id(value):
    try:
        parsed = int(value)
        return parsed if parsed > 0 else None
    except (ValueError, TypeError):
        return None


def get_organisation_for_user(user):
    """Return the UserProfile (organisation) to use for filtering orders/products. Agents see their organisation's data."""
    if user.is_superuser:
        return None
    if getattr(user, "is_agent", False):
        try:
            return Agent.objects.get(user=user).organisation
        except Agent.DoesNotExist:
            return user.userprofile
    return user.userprofile


class OrderListView(LoginRequiredMixin, generic.ListView):
    template_name = "orders/order_list.html"
    context_object_name = "order_list"

    def get_queryset(self):
        user = self.request.user
        org_id = None
        org_id_raw = self.request.GET.get("organisation")
        if org_id_raw is not None and org_id_raw != "":
            try:
                org_id = int(org_id_raw)
            except (TypeError, ValueError):
                org_id = None
        agent_id = None
        agent_id_raw = self.request.GET.get("agent")
        if agent_id_raw is not None and agent_id_raw != "":
            try:
                agent_id = int(agent_id_raw)
            except (TypeError, ValueError):
                agent_id = None
        base = orders.objects.select_related("organisation", "organisation__user", "lead", "lead__agent", "lead__agent__user")
        if user.is_superuser:
            qs = base
            if org_id is not None:
                qs = qs.filter(organisation_id=org_id)
            if agent_id is not None:
                qs = qs.filter(lead__agent_id=agent_id)
            return qs.order_by("-creation_date")
        org = get_organisation_for_user(user)
        if org is None:
            return base.order_by("-creation_date")
        qs = base.filter(organisation=org)
        # Agent only sees orders where the lead is assigned to them
        if user.is_agent:
            try:
                agent_obj = Agent.objects.get(user=user)
                qs = qs.filter(lead__agent=agent_obj)
            except Agent.DoesNotExist:
                qs = qs.none()
        elif agent_id is not None and (user.is_superuser or user.is_organisor):
            qs = qs.filter(lead__agent_id=agent_id)
        return qs.order_by("-creation_date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = context.get("order_list") or context.get("object_list") or self.get_queryset()
        today = timezone.now().date()
        active_orders = []
        completed_orders = []
        for o in qs:
            if o.is_cancelled:
                continue
            order_day_date = o.order_day.date() if hasattr(o.order_day, "date") else o.order_day
            if order_day_date >= today:
                active_orders.append(o)
            else:
                completed_orders.append(o)
        context["active_orders"] = active_orders
        context["completed_orders"] = completed_orders
        context["cancelled_orders"] = [o for o in qs if o.is_cancelled]
        # Filter which sections to show (default: all)
        get = self.request.GET
        context["show_active"] = get.get("show_active", "1") == "1"
        context["show_completed"] = get.get("show_completed", "1") == "1"
        context["show_cancelled"] = get.get("show_cancelled", "1") == "1"
        if self.request.user.is_superuser or self.request.user.is_organisor:
            from leads.models import UserProfile
            selected_org_id = None
            org_raw = self.request.GET.get("organisation", "")
            if org_raw is not None and org_raw != "":
                try:
                    selected_org_id = int(org_raw)
                except (TypeError, ValueError):
                    selected_org_id = None
            selected_agent_id = None
            agent_raw = self.request.GET.get("agent", "")
            if agent_raw is not None and agent_raw != "":
                try:
                    selected_agent_id = int(agent_raw)
                except (TypeError, ValueError):
                    selected_agent_id = None
            context["selected_organisation_id"] = selected_org_id if selected_org_id is not None else ""
            context["selected_agent_id"] = selected_agent_id if selected_agent_id is not None else ""
            if self.request.user.is_superuser:
                # Organisations: all organisors except admin (so admin doesn't see themselves)
                org_qs = UserProfile.objects.filter(user__is_organisor=True).select_related("user").order_by("user__username")
                profile = getattr(self.request.user, "userprofile", None)
                if profile:
                    org_qs = org_qs.exclude(pk=profile.pk)
                context["organisations"] = org_qs
                context["show_organisation_filter"] = True
                # Agents: only for the selected organisation (so admin sees that org's agents)
                if selected_org_id is not None:
                    context["agents"] = Agent.objects.filter(organisation_id=selected_org_id).select_related("user").order_by("user__username")
                else:
                    context["agents"] = []
            else:
                context["organisations"] = []
                context["show_organisation_filter"] = False
                org = get_organisation_for_user(self.request.user)
                context["agents"] = Agent.objects.filter(organisation=org).select_related("user").order_by("user__username") if org else []
        else:
            context["show_organisation_filter"] = False
            context["organisations"] = []
            context["agents"] = []
            context["selected_organisation_id"] = context["selected_agent_id"] = ""
        return context

class OrderDetailView(LoginRequiredMixin, generic.DetailView):
    model = orders
    template_name = "orders/order_detail.html"
    context_object_name = "order"

    def get_queryset(self):
        qs = orders.objects.select_related(
            "organisation", "organisation__user",
            "lead", "lead__agent", "lead__agent__user",
        )
        if self.request.user.is_superuser:
            return qs
        org = get_organisation_for_user(self.request.user)
        if not org:
            return qs.none()
        qs = qs.filter(organisation=org)
        if self.request.user.is_agent:
            try:
                agent_obj = Agent.objects.get(user=self.request.user)
                qs = qs.filter(lead__agent=agent_obj)
            except Agent.DoesNotExist:
                qs = qs.none()
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.get_object()
        order_items = OrderProduct.objects.filter(order=order)

        # Calculate total order price
        total_order_price = sum(item.total_price for item in order_items)

        org = get_organisation_for_user(self.request.user)
        if org:
            context['leads'] = Lead.objects.filter(organisation=org)
            context['products'] = ProductsAndStock.objects.filter(organisation=org)
        else:
            context['leads'] = Lead.objects.none()
            context['products'] = ProductsAndStock.objects.none()
        context['order_items'] = order_items
        context['total_order_price'] = total_order_price  # Pass total order price to template
        return context



class OrderCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = "orders/order_create.html"
    form_class = OrderModelForm
    model = orders

    def get_success_url(self):
        return reverse("orders:order-list")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = self.request.user
        if user.is_superuser:
            from django.forms import ModelChoiceField
            org_qs = UserProfile.objects.filter(user__is_organisor=True).select_related("user").order_by("user__username")
            profile = getattr(user, "userprofile", None)
            if profile:
                org_qs = org_qs.exclude(pk=profile.pk)
            form.fields["organisation"] = ModelChoiceField(
                queryset=org_qs,
                required=True,
                label="Organisation",
                empty_label="-- Select organisation --"
            )
            form.fields["organisation"].widget.attrs["id"] = "id_organisation"
            selected_org = valid_id(self.request.POST.get("organisation") or self.request.GET.get("organisation"))
            selected_agent = valid_id(self.request.POST.get("filter_agent") or self.request.GET.get("agent"))
            if selected_agent:
                form.fields["lead"].queryset = Lead.objects.filter(organisation_id=selected_org, agent_id=selected_agent).select_related("organisation").order_by("first_name", "last_name")
            elif selected_org:
                form.fields["lead"].queryset = Lead.objects.filter(organisation_id=selected_org).select_related("organisation").order_by("first_name", "last_name")
            else:
                form.fields["lead"].queryset = Lead.objects.none()
            form.fields["lead"].required = True
            form.fields["order_day"].required = True
            form.fields["order_name"].required = True
            form.fields["order_description"].required = True
            from collections import OrderedDict
            fields = OrderedDict([("organisation", form.fields.pop("organisation"))])
            fields.update(form.fields)
            form.fields = fields
        elif user.is_organisor:
            # Organisor: same as admin but no organisation (they are the org); agents/leads/products from their org
            selected_agent = valid_id(self.request.POST.get("filter_agent") or self.request.GET.get("agent"))
            org_profile = user.userprofile
            if selected_agent:
                form.fields["lead"].queryset = Lead.objects.filter(organisation=org_profile, agent_id=selected_agent).select_related("organisation").order_by("first_name", "last_name")
            else:
                form.fields["lead"].queryset = Lead.objects.filter(organisation=org_profile).select_related("organisation").order_by("first_name", "last_name")
            form.fields["lead"].required = True
            form.fields["order_day"].required = True
            form.fields["order_name"].required = True
            form.fields["order_description"].required = True
        elif user.is_agent:
            # Agent: only leads assigned to them
            try:
                agent_obj = Agent.objects.get(user=user)
                form.fields["lead"].queryset = Lead.objects.filter(agent=agent_obj).select_related("organisation").order_by("first_name", "last_name")
            except Agent.DoesNotExist:
                form.fields["lead"].queryset = Lead.objects.none()
            form.fields["lead"].required = True
            form.fields["order_day"].required = True
            form.fields["order_name"].required = True
            form.fields["order_description"].required = True
        return form

    def get_initial(self):
        initial = super().get_initial()
        if self.request.user.is_superuser:
            org = self.request.GET.get("organisation")
            if org:
                try:
                    initial["organisation"] = int(org)
                except (TypeError, ValueError):
                    pass
        return initial

    def form_valid(self, form):
        product_formset = self.get_context_data()['product_formset']
        if not product_formset.is_valid():
            return self.form_invalid(form)
        try:
            with transaction.atomic():
                order = form.save(commit=False)
                order.organisation = (form.cleaned_data['organisation'] if self.request.user.is_superuser
                                      else get_organisation_for_user(self.request.user))
                order._current_user = self.request.user
                order.save()
                self.object = order
                product_formset.instance = order
                product_formset.save()
                OrderFinanceReport.objects.update_or_create(
                    order=order, defaults={'earned_amount': order.total_order_price},
                )
                users_to_notify = {order.organisation.user}
                if order.lead_id and order.lead.agent_id:
                    users_to_notify.add(order.lead.agent.user)
                for user in users_to_notify:
                    Notification.objects.create(
                        user=user, title='An order was created',
                        message=f'Order "{order.order_name}" has been created.',
                        action_url=reverse('orders:order-detail', kwargs={'pk': order.pk}),
                        action_label='View Order',
                    )
                log_activity(
                    self.request.user, ACTION_ORDER_CREATED, object_type='order',
                    object_id=order.pk, object_repr=f'Order: {order.order_name}',
                    organisation=order.organisation,
                    affected_agent=getattr(order.lead, 'agent', None),
                )
        except ValidationError as error:
            self.object = None
            form.instance.pk = None
            form.add_error(None, error)
            return self.form_invalid(form)
        messages.success(self.request, 'Order created successfully.')
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        selected_org = valid_id(self.request.POST.get("organisation") or self.request.GET.get("organisation"))
        selected_agent = valid_id(self.request.POST.get("filter_agent") or self.request.GET.get("agent"))
        if user.is_superuser:
            org_qs = UserProfile.objects.filter(user__is_organisor=True).select_related("user").order_by("user__username")
            profile = getattr(user, "userprofile", None)
            if profile:
                org_qs = org_qs.exclude(pk=profile.pk)
            context["create_organisations"] = org_qs
            context["selected_organisation_id"] = str(selected_org) if selected_org else ""
            context["selected_agent_id"] = str(selected_agent) if selected_agent else ""
            if selected_org:
                context["create_agents"] = Agent.objects.filter(organisation_id=selected_org).select_related("user").order_by("user__username")
                context["create_products"] = ProductsAndStock.objects.filter(organisation_id=selected_org)
            else:
                context["create_agents"] = []
                context["create_products"] = ProductsAndStock.objects.none()
        elif user.is_organisor:
            org_profile = user.userprofile
            context["create_organisations"] = []
            context["selected_organisation_id"] = ""
            context["selected_agent_id"] = str(selected_agent) if selected_agent else ""
            context["create_agents"] = Agent.objects.filter(organisation=org_profile).select_related("user").order_by("user__username")
            context["create_products"] = ProductsAndStock.objects.filter(organisation=org_profile)
        else:
            context["create_organisations"] = []
            context["create_agents"] = []
            context["selected_organisation_id"] = context["selected_agent_id"] = ""
            org = get_organisation_for_user(user)
            context["create_products"] = ProductsAndStock.objects.filter(organisation=org) if org else ProductsAndStock.objects.none()
        org = get_organisation_for_user(user)
        context['leads'] = Lead.objects.filter(organisation=org) if org else Lead.objects.none()
        context['products'] = ProductsAndStock.objects.filter(organisation=org) if org else ProductsAndStock.objects.none()
        if not hasattr(self, '_product_formset'):
            self._product_formset = OrderProductFormSet(
                self.request.POST or None, instance=getattr(self, 'object', None),
            )
        context['product_formset'] = self._product_formset
        products_qs = context.get("create_products")
        if products_qs is None:
            org = get_organisation_for_user(self.request.user)
            products_qs = ProductsAndStock.objects.filter(organisation=org) if org else ProductsAndStock.objects.none()
        for form in context['product_formset']:
            form.fields['product'].queryset = products_qs
        context["order_categories"] = Category.objects.filter(productsandstock__in=products_qs).distinct().order_by("name")
        context["order_subcategories"] = SubCategory.objects.filter(category__in=context["order_categories"]).select_related("category").order_by("category__name", "name")
        return context






class OrderUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = "orders/order_update.html"
    form_class = OrderModelForm

    def get_success_url(self):
        return reverse("orders:order-list")

    def get_queryset(self):
        qs = orders.objects.select_related("organisation", "organisation__user", "lead", "lead__agent")
        if self.request.user.is_superuser:
            return qs
        org = get_organisation_for_user(self.request.user)
        if not org:
            return qs.none()
        qs = qs.filter(organisation=org)
        if self.request.user.is_agent:
            try:
                agent_obj = Agent.objects.get(user=self.request.user)
                qs = qs.filter(lead__agent=agent_obj)
            except Agent.DoesNotExist:
                qs = qs.none()
        return qs

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        order = self.get_object()
        user = self.request.user
        if user.is_superuser:
            selected_org = order.organisation_id
            selected_agent = valid_id(self.request.POST.get("filter_agent") or (order.lead.agent_id if order.lead else None))
            if selected_agent:
                form.fields["lead"].queryset = Lead.objects.filter(organisation=order.organisation, agent_id=selected_agent).select_related("organisation").order_by("first_name", "last_name")
            elif selected_org:
                form.fields["lead"].queryset = Lead.objects.filter(organisation_id=selected_org).select_related("organisation").order_by("first_name", "last_name")
            else:
                form.fields["lead"].queryset = Lead.objects.filter(organisation_id=order.organisation_id).select_related("organisation").order_by("first_name", "last_name")
        elif user.is_organisor:
            selected_agent = valid_id(self.request.POST.get("filter_agent") or self.request.GET.get("agent") or (order.lead.agent_id if order.lead else None))
            if selected_agent:
                form.fields["lead"].queryset = Lead.objects.filter(organisation=order.organisation, agent_id=selected_agent).select_related("organisation").order_by("first_name", "last_name")
            else:
                form.fields["lead"].queryset = Lead.objects.filter(organisation=order.organisation).select_related("organisation").order_by("first_name", "last_name")
        elif user.is_agent:
            try:
                agent_obj = Agent.objects.get(user=user)
                form.fields["lead"].queryset = Lead.objects.filter(agent=agent_obj).select_related("organisation").order_by("first_name", "last_name")
            except Agent.DoesNotExist:
                form.fields["lead"].queryset = Lead.objects.none()
        else:
            form.fields["lead"].queryset = Lead.objects.filter(organisation=order.organisation).select_related("organisation").order_by("first_name", "last_name")
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.get_object()
        user = self.request.user
        org_id = str(order.organisation_id)
        agent_id = str(order.lead.agent_id) if order.lead and order.lead.agent_id else ""
        selected_org = org_id
        selected_agent = valid_id(self.request.POST.get("filter_agent") or self.request.GET.get("agent") or agent_id)
        if user.is_superuser:
            org_qs = UserProfile.objects.filter(user__is_organisor=True).select_related("user").order_by("user__username")
            profile = getattr(user, "userprofile", None)
            if profile:
                org_qs = org_qs.exclude(pk=profile.pk)
            context["create_organisations"] = org_qs
            context["selected_organisation_id"] = str(selected_org) if selected_org else ""
            context["selected_agent_id"] = str(selected_agent) if selected_agent else ""
            context["create_agents"] = Agent.objects.filter(organisation_id=order.organisation_id).select_related("user").order_by("user__username")
            context["create_products"] = ProductsAndStock.objects.filter(organisation_id=order.organisation_id)
        elif user.is_organisor:
            context["create_organisations"] = []
            context["selected_organisation_id"] = ""
            context["selected_agent_id"] = str(selected_agent) if selected_agent else ""
            context["create_agents"] = Agent.objects.filter(organisation=order.organisation).select_related("user").order_by("user__username")
            context["create_products"] = ProductsAndStock.objects.filter(organisation=order.organisation)
        else:
            context["create_organisations"] = []
            context["create_agents"] = []
            context["selected_organisation_id"] = context["selected_agent_id"] = ""
            org = get_organisation_for_user(user)
            context["create_products"] = ProductsAndStock.objects.filter(organisation=org) if org else ProductsAndStock.objects.none()
        org = get_organisation_for_user(user)
        context["leads"] = Lead.objects.filter(organisation=org) if org else Lead.objects.none()
        context["products"] = ProductsAndStock.objects.filter(organisation=org) if org else ProductsAndStock.objects.none()
        if not hasattr(self, '_product_formset'):
            self._product_formset = OrderProductFormSet(
                self.request.POST or None, instance=getattr(self, 'object', None),
            )
        context['product_formset'] = self._product_formset
        products_qs = context["create_products"]
        for form in context["product_formset"]:
            form.fields["product"].queryset = products_qs
        context["order_categories"] = Category.objects.filter(productsandstock__in=products_qs).distinct().order_by("name")
        context["order_subcategories"] = SubCategory.objects.filter(category__in=context["order_categories"]).select_related("category").order_by("category__name", "name")
        return context

    def form_valid(self, form):
        product_formset = self.get_context_data()['product_formset']
        if not product_formset.is_valid():
            return self.form_invalid(form)
        try:
            with transaction.atomic():
                current = orders.objects.select_for_update().get(pk=self.object.pk)
                form.instance.is_cancelled = current.is_cancelled
                form.instance._current_user = self.request.user
                self.object = form.save()
                product_formset.instance = self.object
                product_formset.save()
                OrderFinanceReport.objects.update_or_create(
                    order=self.object, defaults={'earned_amount': self.object.total_order_price},
                )
                log_activity(
                    self.request.user, ACTION_ORDER_UPDATED, object_type='order',
                    object_id=self.object.pk, object_repr=f'Order: {self.object.order_name}',
                    organisation=self.object.organisation,
                    affected_agent=getattr(self.object.lead, 'agent', None),
                )
        except ValidationError as error:
            form.add_error(None, error)
            return self.form_invalid(form)
        messages.success(self.request, 'Order updated successfully.')
        return HttpResponseRedirect(self.get_success_url())

class OrderCancelView(LoginRequiredMixin, View):
    success_url = reverse_lazy('orders:order-list')

    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')
        org = get_organisation_for_user(self.request.user)
        if self.request.user.is_superuser:
            qs = orders.objects.all()
        elif org:
            qs = orders.objects.filter(organisation=org)
            if self.request.user.is_agent:
                try:
                    agent_obj = Agent.objects.get(user=self.request.user)
                    qs = qs.filter(lead__agent=agent_obj)
                except Agent.DoesNotExist:
                    qs = orders.objects.none()
        else:
            qs = orders.objects.none()
        return get_object_or_404(qs, pk=pk)

    def post(self, request, *args, **kwargs):
        return self.cancel_order()

    def cancel_order(self):
        order = self.get_object()

        if order.is_cancelled:
            # If the order is already canceled, provide feedback or redirect
            messages.error(self.request, 'This order has already been canceled.')
            return HttpResponseRedirect(self.success_url)
        
        try:
            with transaction.atomic():
                affected_agent = getattr(getattr(order, 'lead', None), 'agent', None)
                log_activity(
                    self.request.user,
                    ACTION_ORDER_CANCELLED,
                    object_type='order',
                    object_id=order.pk,
                    object_repr=f"Order: {order.order_name}",
                    organisation=order.organisation,
                    affected_agent=affected_agent,
                )
                # Stock will be automatically restored by signal when is_cancelled is set to True
                order.is_cancelled = True
                order.save()
                
        except Exception as e:
            # Handle any exceptions that may occur
            # You can log the error or provide feedback to the user
            messages.error(self.request, 'An error occurred while canceling the order.')
            return HttpResponseRedirect(self.success_url)
        
        messages.success(self.request, 'Order cancelled successfully.')
        return HttpResponseRedirect(self.success_url)

class OrderDeleteView(LoginRequiredMixin, generic.DeleteView):
    template_name = "orders/order_delete.html"

    def get_success_url(self):
        return reverse("orders:order-list")

    def get_queryset(self):
        if self.request.user.is_superuser:
            return orders.objects.all()
        org = get_organisation_for_user(self.request.user)
        if not org:
            return orders.objects.none()
        qs = orders.objects.filter(organisation=org)
        if self.request.user.is_agent:
            try:
                agent_obj = Agent.objects.get(user=self.request.user)
                qs = qs.filter(lead__agent=agent_obj)
            except Agent.DoesNotExist:
                qs = orders.objects.none()
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        org = get_organisation_for_user(self.request.user)
        context['leads'] = Lead.objects.filter(organisation=org) if org else Lead.objects.none()
        context['products'] = ProductsAndStock.objects.filter(organisation=org) if org else ProductsAndStock.objects.none()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if "cancel_order" in request.POST:
            return self.cancel_order()
        else:
            return super().post(request, *args, **kwargs)

    def cancel_order(self):
        order = self.get_object()

        if order.is_cancelled:
            messages.error(self.request, 'This order has already been canceled.')
            return HttpResponseRedirect(self.get_success_url())
        
        affected_agent = getattr(getattr(order, 'lead', None), 'agent', None)
        log_activity(
            self.request.user,
            ACTION_ORDER_CANCELLED,
            object_type='order',
            object_id=order.pk,
            object_repr=f"Order: {order.order_name}",
            organisation=order.organisation,
            affected_agent=affected_agent,
        )
        # Stock will be automatically restored by signal when is_cancelled is set to True
        order.is_cancelled = True
        order.save()
        messages.success(self.request, 'Order cancelled successfully.')
        return HttpResponseRedirect(self.get_success_url())
