from django.shortcuts import render, redirect, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from .models import ProductsAndStock
from agents.mixins import OrganisorAndLoginRequiredMixin
from .forms import ProductAndStockModelForm
from django.core.mail import send_mail

class ProductAndStockListView(OrganisorAndLoginRequiredMixin, generic.ListView):
	template_name = "ProductsAndStock/ProductAndStock_list.html"

	def get_queryset(self):
		organisation = self.request.user.userprofile
		return ProductsAndStock.objects.filter(organisation=organisation)
	
class ProductAndStockDetailView(OrganisorAndLoginRequiredMixin, generic.DetailView):
    template_name = "ProductsAndStock/ProductAndStock_detail.html"
    context_object_name = "ProductAndStock"
    
    def get_queryset(self):
        organisation = self.request.user.userprofile
        return ProductsAndStock.objects.filter(organisation=organisation)
    
class ProductAndStockCreateView(OrganisorAndLoginRequiredMixin,generic.CreateView):
    template_name = "ProductsAndStock/ProductAndStock_create.html"
    form_class = ProductAndStockModelForm

    def get_success_url(self):
        return reverse("ProductsAndStock:ProductAndStock-list")
    
    def form_valid(self, form):
        ProductsAndStock = form.save(commit=False)
        ProductsAndStock.organisation = self.request.user.userprofile
        ProductsAndStock.save()
        send_mail(
           subject="A ProductAndStock has been created",
            message="Go to the site to see the new ProductsAndStock",
            from_email="test@test.com",
            recipient_list=["test2@test.com"]
        )
        return super(ProductAndStockCreateView, self).form_valid(form)
    
class ProductAndStockUpdateView(OrganisorAndLoginRequiredMixin, generic.UpdateView):
    template_name = "ProductsAndStock/ProductAndStock_update.html"
    form_class = ProductAndStockModelForm

    def get_success_url(self):
        return reverse("ProductsAndStock:ProductAndStock-list")
    
    def get_queryset(self):
        organisation = self.request.user.userprofile
        return ProductsAndStock.objects.filter(organisation=organisation)

class ProductAndStockDeleteView(OrganisorAndLoginRequiredMixin, generic.DeleteView):
    template_name = "ProductsAndStock/ProductAndStock_delete.html"
    
    def get_success_url(self):
        return reverse("ProductsAndStock:ProductAndStock-list")
    
    def get_queryset(self):
        organisation = self.request.user.userprofile
        return ProductsAndStock.objects.filter(organisation=organisation)
    