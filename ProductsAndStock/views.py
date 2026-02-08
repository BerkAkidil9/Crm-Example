from django.shortcuts import render, redirect, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.http import JsonResponse
from django.contrib import messages
from django.db import transaction, models
from django.db.models import F, Case, When, Value, IntegerField
from .models import ProductsAndStock, Category, SubCategory, PriceHistory, SalesStatistics, StockAlert, StockRecommendation
from leads.models import UserProfile
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
				# Agent sees products from their organisation (via Agent.organisation)
				agent_organisation = self.request.user.agent.organisation
				queryset = ProductsAndStock.objects.filter(organisation=agent_organisation)
			except Exception:
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
		
		# Filter by product name (case-insensitive partial match)
		search = (self.request.GET.get('search') or self.request.GET.get('name') or '').strip()
		if search:
			queryset = queryset.filter(product_name__icontains=search)
		
		# Admin only: filter by organisation (organisor)
		if self.request.user.is_superuser:
			organisation_id = self.request.GET.get('organisation')
			if organisation_id:
				queryset = queryset.filter(organisation_id=organisation_id)
		
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
		
		# Admin only: only organisors (exclude superuser/admin) in filter dropdown
		organisations = []
		selected_organisation_id = self.request.GET.get('organisation') or ''
		if self.request.user.is_superuser:
			organisations = UserProfile.objects.filter(
				user__is_organisor=True,
				user__is_superuser=False,
			).select_related('user').order_by('user__username')
		
		search_query = (self.request.GET.get('search') or self.request.GET.get('name') or '').strip()
		context.update({
			'total_products': total_products,
			'total_quantity': total_quantity,
			'total_value': total_value,
			'categories': categories,
			'subcategories': subcategories,
			'selected_category_id': selected_category_id,
			'selected_subcategory_id': self.request.GET.get('subcategory'),
			'organisations': organisations,
			'selected_organisation_id': selected_organisation_id,
			'search_query': search_query,
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
                    
                    # Update product price (signal won't create PriceHistory; we add one with custom reason)
                    product.product_price = new_price
                    product._skip_price_history_signal = True
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


class ProductChartsView(OrganisorAndLoginRequiredMixin, generic.TemplateView):
    template_name = "ProductsAndStock/product_charts.html"

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return ProductsAndStock.objects.all()
        elif user.is_organisor:
            return ProductsAndStock.objects.filter(organisation=user.userprofile)
        return ProductsAndStock.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        products = list(self.get_queryset())
        # Stock status counts (same logic as dashboard)
        out_of_stock = sum(1 for p in products if p.product_quantity <= 0)
        low_stock = sum(1 for p in products if p.is_low_stock and p.product_quantity > 0)
        overstock = sum(1 for p in products if p.minimum_stock_level and p.product_quantity > p.minimum_stock_level * 10)
        in_stock = sum(1 for p in products if p.product_quantity > p.minimum_stock_level and (not p.minimum_stock_level or p.product_quantity <= p.minimum_stock_level * 10))
        context['chart_stock_labels'] = ['Out of Stock', 'Low Stock', 'In Stock', 'Overstock']
        context['chart_stock_data'] = [out_of_stock, low_stock, in_stock, overstock]
        context['chart_stock_colors'] = ['#ef4444', '#f97316', '#22c55e', '#eab308']
        import json
        from collections import defaultdict
        context['chart_stock_labels_json'] = json.dumps(context['chart_stock_labels'])
        context['chart_stock_data_json'] = json.dumps(context['chart_stock_data'])
        context['chart_stock_colors_json'] = json.dumps(context['chart_stock_colors'])
        # By category
        by_cat = defaultdict(lambda: {'count': 0, 'value': 0})
        for p in products:
            name = p.category.name
            by_cat[name]['count'] += 1
            by_cat[name]['value'] += p.total_value
        context['chart_category_labels'] = list(by_cat.keys())
        context['chart_category_counts'] = [by_cat[k]['count'] for k in by_cat]
        context['chart_category_values'] = [round(by_cat[k]['value'], 2) for k in by_cat]
        context['chart_category_labels_json'] = json.dumps(context['chart_category_labels'])
        context['chart_category_counts_json'] = json.dumps(context['chart_category_counts'])
        context['chart_category_values_json'] = json.dumps(context['chart_category_values'])
        # Top products by total value (max 10)
        by_value = sorted(products, key=lambda x: x.total_value, reverse=True)[:10]
        context['chart_top_labels'] = [p.product_name[:18] + ('..' if len(p.product_name) > 18 else '') for p in by_value]
        context['chart_top_data'] = [round(p.total_value, 2) for p in by_value]
        context['chart_top_labels_json'] = json.dumps(context['chart_top_labels'])
        context['chart_top_data_json'] = json.dumps(context['chart_top_data'])
        # Top selling products (by units sold) - max 10
        by_sales = sorted(products, key=lambda x: x.total_sales_count, reverse=True)[:10]
        context['chart_sales_labels'] = [p.product_name[:18] + ('..' if len(p.product_name) > 18 else '') for p in by_sales]
        context['chart_sales_data'] = [p.total_sales_count for p in by_sales]
        context['chart_sales_revenue_data'] = [round(p.total_revenue_from_sales, 2) for p in by_sales]
        context['chart_has_sales'] = any(p.total_sales_count > 0 for p in products)
        context['chart_sales_labels_json'] = json.dumps(context['chart_sales_labels'])
        context['chart_sales_data_json'] = json.dumps(context['chart_sales_data'])
        context['chart_sales_revenue_data_json'] = json.dumps(context['chart_sales_revenue_data'])
        # Summary
        context['total_products'] = len(products)
        context['total_value'] = round(sum(p.total_value for p in products), 2)
        context['total_profit'] = round(sum(p.total_profit for p in products if p.cost_price > 0), 2)
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
        context['low_stock_products'] = products.filter(product_quantity__lte=F('minimum_stock_level')).exclude(product_quantity=0).count()
        context['out_of_stock_products'] = products.filter(product_quantity=0).count()
        context['overstock_products'] = products.filter(product_quantity__gt=F('minimum_stock_level') * 10).count()
        # In Stock = quantity > min and not overstock (min < qty <= min*10)
        context['in_stock_products'] = products.filter(
            product_quantity__gt=F('minimum_stock_level'),
            product_quantity__lte=F('minimum_stock_level') * 10
        ).count()
        
        # Top Selling Products (only products with at least 1 sale, sorted by sales count)
        products_with_sales = [p for p in products if p.total_sales_count > 0]
        context['top_selling_products'] = sorted(
            products_with_sales,
            key=lambda x: x.total_sales_count,
            reverse=True
        )[:5]
        
        # Recent Alerts: kritiklik yuksekten dusuge (CRITICAL -> HIGH -> MEDIUM -> LOW), sonra en yeni tarih
        severity_order = Case(
            When(severity='CRITICAL', then=Value(0)),
            When(severity='HIGH', then=Value(1)),
            When(severity='MEDIUM', then=Value(2)),
            When(severity='LOW', then=Value(3)),
            default=Value(4),
            output_field=IntegerField(),
        )
        context['recent_alerts'] = StockAlert.objects.filter(
            product__in=products,
            is_resolved=False
        ).annotate(severity_order=severity_order).order_by('severity_order', '-created_at')[:20]
        
        # Stock Recommendations: sadece sorun hala gecerliyse goster, urun basina tek oneri (en onemli)
        # Ayni urunde hem DISCOUNT hem REDUCE_STOCK olmasin; confidence_score ile sirali, urun basina ilk gelen
        recs_qs = StockRecommendation.objects.filter(
            product__in=products,
            is_applied=False
        ).select_related('product').order_by('-confidence_score', '-created_at')
        seen_product_ids = set()
        relevant_recs = []
        for rec in recs_qs:
            if not (
                (rec.recommendation_type == 'RESTOCK' and rec.product.is_low_stock and rec.product.product_quantity > 0) or
                (rec.recommendation_type == 'DISCOUNT' and rec.product.product_quantity > rec.product.minimum_stock_level * 5) or
                (rec.recommendation_type == 'REDUCE_STOCK' and rec.product.product_quantity > rec.product.minimum_stock_level * 10)
            ):
                continue
            if rec.product_id in seen_product_ids:
                continue
            seen_product_ids.add(rec.product_id)
            relevant_recs.append(rec)
        context['stock_recommendations'] = relevant_recs
        
        # Critical Alerts: sadece urun hala kritik durumdaysa say ve listele (duzelince dusar)
        # Ayni urun birden fazla alert kaydi ile tekrar etmesin: urun basina bir tane (en guncel alert)
        critical_alerts_qs = StockAlert.objects.filter(
            product__in=products,
            is_resolved=False,
            severity='CRITICAL'
        ).select_related('product').order_by('-created_at')
        still_critical = [
            a for a in critical_alerts_qs
            if a.product.product_quantity <= 0
            or (a.product.minimum_stock_level and a.product.product_quantity <= a.product.minimum_stock_level / 2)
        ]
        seen_product_ids = set()
        critical_alerts_list = []
        for a in still_critical:
            if a.product_id not in seen_product_ids:
                seen_product_ids.add(a.product_id)
                critical_alerts_list.append(a)
        context['critical_alerts_count'] = len(critical_alerts_list)
        context['critical_alerts_list'] = critical_alerts_list
        
        # Products with Active Alerts: limit yok, sadece alert durumu hala gecerli olanlar (sorun devam ediyorsa)
        products_with_unresolved = products.filter(
            stock_alerts__is_resolved=False
        ).distinct()
        products_with_alerts = [
            p for p in products_with_unresolved
            if p.product_quantity <= 0
            or p.is_low_stock
            or (p.minimum_stock_level and p.product_quantity > p.minimum_stock_level * 10)
        ]
        context['products_with_alerts'] = products_with_alerts
        
        return context
    