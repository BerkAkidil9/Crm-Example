from django.shortcuts import render, redirect, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.http import JsonResponse
from django.contrib import messages
from django.db import transaction
from django.db import models
from .models import ProductsAndStock, Category, SubCategory, PriceHistory, SalesStatistics, StockAlert, StockRecommendation
from agents.mixins import OrganisorAndLoginRequiredMixin, AgentAndOrganisorLoginRequiredMixin, ProductsAndStockAccessMixin
from .forms import ProductAndStockModelForm, AdminProductAndStockModelForm
from .bulk_price_form import BulkPriceUpdateForm
from django.core.mail import send_mail

class ProductAndStockListView(ProductsAndStockAccessMixin, generic.ListView):
	template_name = "ProductsAndStock/ProductAndStock_list.html"

	def get_queryset(self):
		# Admin can see all products
		if self.request.user.is_superuser:
			queryset = ProductsAndStock.objects.all()
		# Organisors and Agents can see products from their organisation
		elif self.request.user.is_organisor:
			organisation = self.request.user.userprofile
			queryset = ProductsAndStock.objects.filter(organisation=organisation)
		elif self.request.user.is_agent:
			try:
				# Agent sees products from their organisation (via UserProfile)
				agent_organisation = self.request.user.userprofile
				queryset = ProductsAndStock.objects.filter(organisation=agent_organisation)
			except Exception as e:
				# If agent doesn't exist, return empty queryset
				print(f"Agent access error: {e}")
				print(f"User: {self.request.user.username}")
				print(f"Is agent: {self.request.user.is_agent}")
				queryset = ProductsAndStock.objects.none()
		else:
			queryset = ProductsAndStock.objects.none()
		
		# Apply category filter
		category_id = self.request.GET.get('category')
		if category_id:
			queryset = queryset.filter(category_id=category_id)
		
		# Apply subcategory filter
		subcategory_id = self.request.GET.get('subcategory')
		if subcategory_id:
			queryset = queryset.filter(subcategory_id=subcategory_id)
		
		return queryset
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		products = self.get_queryset()
		
		# Calculate statistics
		total_products = products.count()
		total_quantity = sum(product.product_quantity for product in products)
		total_value = sum(product.product_price * product.product_quantity for product in products)
		
		# Get categories for filter
		categories = Category.objects.all()
		subcategories = SubCategory.objects.none()
		
		# If a category is selected, get its subcategories
		selected_category_id = self.request.GET.get('category')
		if selected_category_id:
			try:
				subcategories = SubCategory.objects.filter(category_id=selected_category_id)
			except (ValueError, TypeError):
				pass
		
		context.update({
			'total_products': total_products,
			'total_quantity': total_quantity,
			'total_value': total_value,
			'categories': categories,
			'subcategories': subcategories,
			'selected_category_id': selected_category_id,
			'selected_subcategory_id': self.request.GET.get('subcategory'),
		})
		
		return context
	
class ProductAndStockDetailView(ProductsAndStockAccessMixin, generic.DetailView):
    template_name = "ProductsAndStock/ProductAndStock_detail.html"
    context_object_name = "ProductAndStock"
    
    def get_queryset(self):
        # Admin can see all products
        if self.request.user.is_superuser:
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
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        
        # Get stock movements for this product (last 10 movements)
        stock_movements = product.stock_movements.all()[:10]
        context['stock_movements'] = stock_movements
        
        # Get price history for this product (last 10 changes)
        price_history = product.price_history.all()[:10]
        context['price_history'] = price_history
        
        return context
    
class ProductAndStockCreateView(OrganisorAndLoginRequiredMixin,generic.CreateView):
    template_name = "ProductsAndStock/ProductAndStock_create.html"
    
    def get_form_class(self):
        user = self.request.user
        if user.is_superuser:
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
        if user.is_superuser:
            return AdminProductAndStockModelForm
        else:
            return ProductAndStockModelForm

    def get_success_url(self):
        return reverse("ProductsAndStock:ProductAndStock-list")
    
    def get_queryset(self):
        user = self.request.user
        # Admin can update all products
        if user.is_superuser:
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
        if user.is_superuser:
            return ProductsAndStock.objects.all()
        # Organisors can delete their own products
        elif user.is_organisor:
            organisation = user.userprofile
            return ProductsAndStock.objects.filter(organisation=organisation)
        else:
            return ProductsAndStock.objects.none()

def get_subcategories(request):
    """AJAX endpoint to get subcategories for a given category"""
    category_id = request.GET.get('category_id')
    
    if category_id:
        try:
            subcategories = SubCategory.objects.filter(category_id=category_id).values('id', 'name')
            return JsonResponse({
                'subcategories': list(subcategories)
            })
        except ValueError:
            return JsonResponse({'error': 'Invalid category ID'}, status=400)
    
    return JsonResponse({'subcategories': []})

class BulkPriceUpdateView(OrganisorAndLoginRequiredMixin, generic.FormView):
    template_name = "ProductsAndStock/bulk_price_update.html"
    form_class = BulkPriceUpdateForm
    success_url = None  # Will be set in get_success_url
    
    def get_success_url(self):
        return reverse("ProductsAndStock:ProductAndStock-list")
    
    def get_queryset(self):
        """Get products that can be updated by current user"""
        user = self.request.user
        if user.is_superuser:
            return ProductsAndStock.objects.all()
        elif user.is_organisor:
            organisation = user.userprofile
            return ProductsAndStock.objects.filter(organisation=organisation)
        else:
            return ProductsAndStock.objects.none()
    
    def form_valid(self, form):
        """Process bulk price update"""
        update_type = form.cleaned_data['update_type']
        category_filter = form.cleaned_data['category_filter']
        category = form.cleaned_data.get('category')
        subcategory = form.cleaned_data.get('subcategory')
        reason = form.cleaned_data.get('reason', 'Bulk price update')
        
        # Get products to update
        products = self.get_queryset()
        
        # Apply filters
        if category_filter == 'CATEGORY' and category:
            products = products.filter(category=category)
        elif category_filter == 'SUBCATEGORY' and subcategory:
            products = products.filter(subcategory=subcategory)
        
        updated_count = 0
        
        try:
            with transaction.atomic():
                for product in products:
                    old_price = product.product_price
                    new_price = old_price
                    
                    # Calculate new price based on update type
                    if update_type == 'PERCENTAGE_INCREASE':
                        percentage = form.cleaned_data['percentage_increase']
                        new_price = old_price * (1 + percentage / 100)
                    elif update_type == 'PERCENTAGE_DECREASE':
                        percentage = form.cleaned_data['percentage_decrease']
                        new_price = old_price * (1 - percentage / 100)
                    elif update_type == 'FIXED_AMOUNT_INCREASE':
                        amount = form.cleaned_data['fixed_amount_increase']
                        new_price = old_price + amount
                    elif update_type == 'FIXED_AMOUNT_DECREASE':
                        amount = form.cleaned_data['fixed_amount_decrease']
                        new_price = old_price - amount
                    elif update_type == 'SET_PRICE':
                        new_price = form.cleaned_data['new_price']
                    
                    # Update product price
                    product.product_price = new_price
                    product.save()
                    
                    # Create price history record
                    price_change = new_price - old_price
                    
                    # Determine change type based on price change
                    if price_change > 0:
                        change_type = 'INCREASE'
                    elif price_change < 0:
                        change_type = 'DECREASE'
                    else:
                        change_type = 'BULK_UPDATE'
                    
                    PriceHistory.objects.create(
                        product=product,
                        old_price=old_price,
                        new_price=new_price,
                        price_change=price_change,
                        change_type=change_type,
                        change_reason=reason,
                        updated_by=self.request.user
                    )
                    
                    updated_count += 1
                
                messages.success(
                    self.request, 
                    f'Successfully updated prices for {updated_count} products.'
                )
                
        except Exception as e:
            messages.error(
                self.request, 
                f'Error updating prices: {str(e)}'
            )
        
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_products'] = self.get_queryset().count()
        return context

class SalesDashboardView(OrganisorAndLoginRequiredMixin, generic.TemplateView):
    template_name = "ProductsAndStock/sales_dashboard.html"
    
    def get_queryset(self):
        """Get products that can be viewed by current user"""
        user = self.request.user
        if user.is_superuser:
            return ProductsAndStock.objects.all()
        elif user.is_organisor:
            organisation = user.userprofile
            return ProductsAndStock.objects.filter(organisation=organisation)
        else:
            return ProductsAndStock.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        products = self.get_queryset()
        
        # Sales Statistics
        context['total_products'] = products.count()
        context['total_value'] = sum(p.total_value for p in products)
        context['total_profit'] = sum(p.total_profit for p in products if p.cost_price > 0)
        context['low_stock_products'] = products.filter(product_quantity__lte=models.F('minimum_stock_level')).count()
        context['out_of_stock_products'] = products.filter(product_quantity=0).count()
        context['in_stock_products'] = products.filter(product_quantity__gt=models.F('minimum_stock_level')).count()
        
        # Top Selling Products (by actual sales count)
        context['top_selling_products'] = sorted(
            products, 
            key=lambda x: x.total_sales_count, 
            reverse=True
        )[:5]
        
        # Recent Alerts
        context['recent_alerts'] = StockAlert.objects.filter(
            product__in=products,
            is_resolved=False
        ).order_by('-created_at')[:10]
        
        # Stock Recommendations
        context['stock_recommendations'] = StockRecommendation.objects.filter(
            product__in=products,
            is_applied=False
        ).order_by('-confidence_score')[:10]
        
        # Critical Alerts Count
        context['critical_alerts_count'] = StockAlert.objects.filter(
            product__in=products,
            is_resolved=False,
            severity='CRITICAL'
        ).count()
        
        # Products with Active Alerts
        context['products_with_alerts'] = products.filter(
            stock_alerts__is_resolved=False
        ).distinct()[:5]
        
        return context
    