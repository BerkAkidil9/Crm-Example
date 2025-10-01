from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic, View
from agents.mixins import OrganisorAndLoginRequiredMixin
from django.core.mail import send_mail
from .models import orders, OrderProduct
from leads.models import Lead
from .forms import OrderModelForm, OrderForm, OrderProductFormSet
from ProductsAndStock.models import ProductsAndStock
from django.http import HttpResponseRedirect
from django.forms import inlineformset_factory
from django.db import transaction
from django.urls import reverse_lazy
from django.contrib import messages
from finance.models import OrderFinanceReport
from django.utils import timezone

class OrderListView(LoginRequiredMixin, generic.ListView):
    template_name = "orders/order_list.html"

    def get_queryset(self):
        return orders.objects.filter(organisation=self.request.user.userprofile)

class OrderDetailView(LoginRequiredMixin, generic.DetailView):
    model = orders
    template_name = "orders/order_detail.html"
    context_object_name = "order"

    def get_queryset(self):
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

    def form_valid(self, form):
        context = self.get_context_data()
        product_formset = context['product_formset']
        if product_formset.is_valid():
            order = form.save(commit=False)
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
        context['leads'] = Lead.objects.filter(organisation=self.request.user.userprofile)
        context['products'] = ProductsAndStock.objects.filter(organisation=self.request.user.userprofile)
        if self.request.POST:
            context['product_formset'] = OrderProductFormSet(self.request.POST)
        else:
            context['product_formset'] = OrderProductFormSet()
        return context






class OrderUpdateView(OrganisorAndLoginRequiredMixin, generic.UpdateView):
    template_name = "orders/order_update.html"
    form_class = OrderModelForm

    def get_success_url(self):
        return reverse("orders:order-list")

    def get_queryset(self):
        organisation = self.request.user.userprofile
        return orders.objects.filter(organisation=organisation)

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

class OrderCancelView(View):
    success_url = reverse_lazy('orders:order-list')

    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')
        return get_object_or_404(orders, pk=pk)

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
