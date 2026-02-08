from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic, View
from agents.mixins import OrganisorAndLoginRequiredMixin
from django.core.mail import send_mail
from .models import orders, OrderProduct
from leads.models import Lead, Agent
from leads.models import UserProfile
from .forms import OrderModelForm, OrderForm, OrderProductFormSet
from ProductsAndStock.models import ProductsAndStock, Category, SubCategory
from django.http import HttpResponseRedirect
from django.forms import inlineformset_factory
from django.db import transaction
from django.urls import reverse_lazy
from django.contrib import messages
from finance.models import OrderFinanceReport
from django.utils import timezone

class OrderListView(LoginRequiredMixin, generic.ListView):
    template_name = "orders/order_list.html"
    context_object_name = "order_list"

    def get_queryset(self):
        user = self.request.user
        org_id = self.request.GET.get("organisation")
        agent_id = self.request.GET.get("agent")
        if user.is_superuser:
            qs = orders.objects.all()
            if org_id:
                qs = qs.filter(organisation_id=org_id)
            if agent_id:
                qs = qs.filter(lead__agent_id=agent_id)
            return qs.order_by("-creation_date")
        qs = orders.objects.filter(organisation=user.userprofile)
        if agent_id and (user.is_superuser or user.is_organisor):
            qs = qs.filter(lead__agent_id=agent_id)
        return qs.order_by("-creation_date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = context.get("order_list") or context.get("object_list") or self.get_queryset()
        context["active_orders"] = [o for o in qs if not o.is_cancelled]
        context["cancelled_orders"] = [o for o in qs if o.is_cancelled]
        if self.request.user.is_superuser or self.request.user.is_organisor:
            from leads.models import UserProfile
            selected_org_id = self.request.GET.get("organisation", "")
            selected_agent_id = self.request.GET.get("agent", "")
            context["selected_organisation_id"] = selected_org_id
            context["selected_agent_id"] = selected_agent_id
            if self.request.user.is_superuser:
                # Organisations: all organisors except admin (so admin doesn't see themselves)
                org_qs = UserProfile.objects.filter(user__is_organisor=True).select_related("user").order_by("user__username")
                profile = getattr(self.request.user, "userprofile", None)
                if profile:
                    org_qs = org_qs.exclude(pk=profile.pk)
                context["organisations"] = org_qs
                context["show_organisation_filter"] = True
                # Agents: only for the selected organisation (so admin sees that org's agents)
                if selected_org_id:
                    context["agents"] = Agent.objects.filter(organisation_id=selected_org_id).select_related("user").order_by("user__username")
                else:
                    context["agents"] = []
            else:
                context["organisations"] = []
                context["show_organisation_filter"] = False
                context["agents"] = Agent.objects.filter(organisation=self.request.user.userprofile).select_related("user").order_by("user__username")
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
        if self.request.user.is_superuser:
            return orders.objects.all()
        return orders.objects.filter(organisation=self.request.user.userprofile)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.get_object()
        order_items = OrderProduct.objects.filter(order=order)

        # Calculate total order price
        total_order_price = sum(item.total_price for item in order_items)

        context['leads'] = Lead.objects.filter(organisation=self.request.user.userprofile)
        context['products'] = ProductsAndStock.objects.filter(organisation=self.request.user.userprofile)
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
        if self.request.user.is_superuser:
            from django.forms import ModelChoiceField
            org_qs = UserProfile.objects.filter(user__is_organisor=True).select_related("user").order_by("user__username")
            profile = getattr(self.request.user, "userprofile", None)
            if profile:
                org_qs = org_qs.exclude(pk=profile.pk)
            form.fields["organisation"] = ModelChoiceField(
                queryset=org_qs,
                required=True,
                label="Organisation",
                empty_label="-- Select organisation --"
            )
            form.fields["organisation"].widget.attrs["id"] = "id_organisation"
            # Lead queryset: only when agent is selected (admin must select agent first to see leads)
            selected_org = self.request.GET.get("organisation")
            selected_agent = self.request.GET.get("agent")
            if selected_agent:
                form.fields["lead"].queryset = Lead.objects.filter(agent_id=selected_agent).select_related("organisation").order_by("first_name", "last_name")
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
        context = self.get_context_data()
        product_formset = context['product_formset']
        if product_formset.is_valid():
            if self.request.user.is_superuser:
                has_product_row = any(
                    f.cleaned_data.get("product") and f.cleaned_data.get("product_quantity")
                    for f in product_formset
                )
                if not has_product_row:
                    messages.error(self.request, "Please add at least one product with quantity.")
                    return self.form_invalid(form)
            order = form.save(commit=False)
            if self.request.user.is_superuser and form.cleaned_data.get("organisation"):
                order.organisation = form.cleaned_data["organisation"]
            else:
                order.organisation = self.request.user.userprofile
            order.creation_date = timezone.now()  # Set the creation date to now
            order.save()
            total_price = 0

            with transaction.atomic():
                for product_form in product_formset:
                    product = product_form.cleaned_data.get('product')
                    quantity = product_form.cleaned_data.get('product_quantity')
                    if product and quantity:
                        # Check if enough stock is available
                        if product.product_quantity >= quantity:
                            order_product = OrderProduct.objects.create(
                                order=order,
                                product=product,
                                product_quantity=quantity,
                                total_price=quantity * product.product_price
                            )
                            total_price += order_product.total_price
                            # Stock will be automatically reduced by signal
                        else:
                            messages.error(self.request, f'Insufficient stock for {product.product_name}. Available: {product.product_quantity}, Required: {quantity}')
                            return self.form_invalid(form)

                # Create OrderFinanceReport entry
                OrderFinanceReport.objects.create(
                    order=order,
                    earned_amount=total_price
                )

                send_mail(
                    subject="An Order has been created",
                    message="Go to the site to see the new Order",
                    from_email="test@test.com",
                    recipient_list=["test2@test.com"]
                )

            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        selected_org = self.request.GET.get("organisation")
        selected_agent = self.request.GET.get("agent")
        if self.request.user.is_superuser:
            org_qs = UserProfile.objects.filter(user__is_organisor=True).select_related("user").order_by("user__username")
            profile = getattr(self.request.user, "userprofile", None)
            if profile:
                org_qs = org_qs.exclude(pk=profile.pk)
            context["create_organisations"] = org_qs
            context["selected_organisation_id"] = selected_org or ""
            context["selected_agent_id"] = selected_agent or ""
            if selected_org:
                context["create_agents"] = Agent.objects.filter(organisation_id=selected_org).select_related("user").order_by("user__username")
                context["create_products"] = ProductsAndStock.objects.filter(organisation_id=selected_org)
            else:
                context["create_agents"] = []
                context["create_products"] = ProductsAndStock.objects.none()
        else:
            context["create_organisations"] = []
            context["create_agents"] = []
            context["selected_organisation_id"] = context["selected_agent_id"] = ""
            context["create_products"] = ProductsAndStock.objects.filter(organisation=self.request.user.userprofile)
        context['leads'] = Lead.objects.filter(organisation=self.request.user.userprofile)
        context['products'] = ProductsAndStock.objects.filter(organisation=self.request.user.userprofile)
        if self.request.POST:
            context['product_formset'] = OrderProductFormSet(self.request.POST)
        else:
            context['product_formset'] = OrderProductFormSet()
        products_qs = context.get("create_products")
        if products_qs is None:
            products_qs = ProductsAndStock.objects.filter(organisation=self.request.user.userprofile)
        for form in context['product_formset']:
            form.fields['product'].queryset = products_qs
        context["order_categories"] = Category.objects.filter(productsandstock__in=products_qs).distinct().order_by("name")
        context["order_subcategories"] = SubCategory.objects.filter(category__in=context["order_categories"]).select_related("category").order_by("category__name", "name")
        return context






class OrderUpdateView(OrganisorAndLoginRequiredMixin, generic.UpdateView):
    template_name = "orders/order_update.html"
    form_class = OrderModelForm

    def get_success_url(self):
        return reverse("orders:order-list")

    def get_queryset(self):
        if self.request.user.is_superuser:
            return orders.objects.all()
        return orders.objects.filter(organisation=self.request.user.userprofile)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        organisation = self.request.user.userprofile
        context['leads'] = Lead.objects.filter(organisation=organisation)
        context['products'] = ProductsAndStock.objects.filter(organisation=organisation)
        return context

    def form_valid(self, form):
        # Save the order without affecting products
        order = form.save()
        return super().form_valid(form)

class OrderCancelView(LoginRequiredMixin, View):
    success_url = reverse_lazy('orders:order-list')

    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')
        qs = orders.objects.all() if self.request.user.is_superuser else orders.objects.filter(organisation=self.request.user.userprofile)
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
                # Stock will be automatically restored by signal when is_cancelled is set to True
                order.is_cancelled = True
                order.save()
                
        except Exception as e:
            # Handle any exceptions that may occur
            # You can log the error or provide feedback to the user
            messages.error(self.request, 'An error occurred while canceling the order.')
            return HttpResponseRedirect(self.success_url)
        
        messages.success(self.request, 'The order was successfully canceled.')
        return HttpResponseRedirect(self.success_url)

class OrderDeleteView(LoginRequiredMixin, generic.DeleteView):
    template_name = "orders/order_delete.html"

    def get_success_url(self):
        return reverse("orders:order-list")

    def get_queryset(self):
        if self.request.user.is_superuser:
            return orders.objects.all()
        return orders.objects.filter(organisation=self.request.user.userprofile)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['leads'] = Lead.objects.filter(organisation=self.request.user.userprofile)
        context['products'] = ProductsAndStock.objects.filter(organisation=self.request.user.userprofile)
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
        
        # Stock will be automatically restored by signal when is_cancelled is set to True
        order.is_cancelled = True
        order.save()
        messages.success(self.request, 'The order was successfully canceled.')
        return HttpResponseRedirect(self.get_success_url())
