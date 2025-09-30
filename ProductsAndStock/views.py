from django.shortcuts import render, redirect, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from .models import ProductsAndStock
from agents.mixins import OrganisorAndLoginRequiredMixin, AgentAndOrganisorLoginRequiredMixin, ProductsAndStockAccessMixin
from .forms import ProductAndStockModelForm, AdminProductAndStockModelForm
from django.core.mail import send_mail

class ProductAndStockListView(ProductsAndStockAccessMixin, generic.ListView):
	template_name = "ProductsAndStock/ProductAndStock_list.html"

	def get_queryset(self):
		# Admin can see all products
		if self.request.user.id == 1 or self.request.user.username == 'berk':
			return ProductsAndStock.objects.all()
		# Organisors and Agents can see products from their organisation
		elif self.request.user.is_organisor:
			organisation = self.request.user.userprofile
			return ProductsAndStock.objects.filter(organisation=organisation)
		elif self.request.user.is_agent:
			try:
				# Agent sees products from their organisation
				agent_organisation = self.request.user.agent.organisation
				return ProductsAndStock.objects.filter(organisation=agent_organisation)
			except Exception as e:
				# If agent doesn't exist, return empty queryset
				print(f"Agent access error: {e}")
				print(f"User: {self.request.user.username}")
				print(f"Is agent: {self.request.user.is_agent}")
				return ProductsAndStock.objects.none()
		else:
			return ProductsAndStock.objects.none()
	
class ProductAndStockDetailView(ProductsAndStockAccessMixin, generic.DetailView):
    template_name = "ProductsAndStock/ProductAndStock_detail.html"
    context_object_name = "ProductAndStock"
    
    def get_queryset(self):
        # Admin can see all products
        if self.request.user.id == 1 or self.request.user.username == 'berk':
            return ProductsAndStock.objects.all()
        # Organisors and Agents can see products from their organisation
        elif self.request.user.is_organisor:
            organisation = self.request.user.userprofile
            return ProductsAndStock.objects.filter(organisation=organisation)
        elif self.request.user.is_agent:
            try:
                # Agent sees products from their organisation
                agent_organisation = self.request.user.agent.organisation
                return ProductsAndStock.objects.filter(organisation=agent_organisation)
            except Exception as e:
                # If agent doesn't exist, return empty queryset
                print(f"Agent access error: {e}")
                print(f"User: {self.request.user.username}")
                print(f"Is agent: {self.request.user.is_agent}")
                return ProductsAndStock.objects.none()
        else:
            return ProductsAndStock.objects.none()
    
class ProductAndStockCreateView(OrganisorAndLoginRequiredMixin,generic.CreateView):
    template_name = "ProductsAndStock/ProductAndStock_create.html"
    
    def get_form_class(self):
        user = self.request.user
        if user.is_superuser or user.id == 1 or user.username == 'berk':
            return AdminProductAndStockModelForm
        else:
            return ProductAndStockModelForm

    def get_success_url(self):
        return reverse("ProductsAndStock:ProductAndStock-list")
    
    def form_valid(self, form):
        product = form.save(commit=False)
        user = self.request.user
        
        # Admin uses the form's organisation field, organisors use their own
        if not (user.is_superuser or user.id == 1 or user.username == 'berk'):
            # Organisors use their own organisation
            try:
                product.organisation = user.userprofile
                # Form'a user_organisation'ı set et (clean metodunda kullanmak için)
                form.user_organisation = user.userprofile
            except:
                from django.contrib import messages
                messages.error(self.request, "User profile not found. Please contact administrator.")
                return self.form_invalid(form)
        # For admin, organisation is already set by the form
            
        product.save()
        send_mail(
           subject="A ProductAndStock has been created",
            message="Go to the site to see the new ProductsAndStock",
            from_email="test@test.com",
            recipient_list=["test2@test.com"]
        )
        return super(ProductAndStockCreateView, self).form_valid(form)
    
class ProductAndStockUpdateView(OrganisorAndLoginRequiredMixin, generic.UpdateView):
    template_name = "ProductsAndStock/ProductAndStock_update.html"
    
    def get_form_class(self):
        user = self.request.user
        if user.is_superuser or user.id == 1 or user.username == 'berk':
            return AdminProductAndStockModelForm
        else:
            return ProductAndStockModelForm

    def get_success_url(self):
        return reverse("ProductsAndStock:ProductAndStock-list")
    
    def get_queryset(self):
        user = self.request.user
        # Admin can update all products
        if user.is_superuser or user.id == 1 or user.username == 'berk':
            return ProductsAndStock.objects.all()
        # Organisors can update their own products
        elif user.is_organisor:
            organisation = user.userprofile
            return ProductsAndStock.objects.filter(organisation=organisation)
        else:
            return ProductsAndStock.objects.none()
    
    def form_valid(self, form):
        user = self.request.user
        
        # Organisors için user_organisation'ı set et (clean metodunda kullanmak için)
        if not (user.is_superuser or user.id == 1 or user.username == 'berk'):
            try:
                form.user_organisation = user.userprofile
            except:
                pass  # Update'de organisation zaten mevcut
        
        return super().form_valid(form)

class ProductAndStockDeleteView(OrganisorAndLoginRequiredMixin, generic.DeleteView):
    template_name = "ProductsAndStock/ProductAndStock_delete.html"
    
    def get_success_url(self):
        return reverse("ProductsAndStock:ProductAndStock-list")
    
    def get_queryset(self):
        user = self.request.user
        # Admin can delete all products
        if user.is_superuser or user.id == 1 or user.username == 'berk':
            return ProductsAndStock.objects.all()
        # Organisors can delete their own products
        elif user.is_organisor:
            organisation = user.userprofile
            return ProductsAndStock.objects.filter(organisation=organisation)
        else:
            return ProductsAndStock.objects.none()
    