from django.contrib import admin
from .models import ProductsAndStock, StockMovement, Category, SubCategory, PriceHistory, SalesStatistics, StockAlert, StockRecommendation
from leads.models import UserProfile


class OrganisorListFilter(admin.SimpleListFilter):
	title = 'Organisor'
	parameter_name = 'organisation'

	def lookups(self, request, model_admin):
		# Organisor olan ve en az bir urunu olan UserProfile'lar (admin'de urun olan tum org'lar)
		org_ids = ProductsAndStock.objects.values_list('organisation_id', flat=True).distinct()
		for profile in UserProfile.objects.filter(pk__in=org_ids).select_related('user').order_by('user__username'):
			label = f"{profile.user.username}"
			if profile.user.email:
				label += f" ({profile.user.email})"
			yield (str(profile.pk), label)

	def queryset(self, request, queryset):
		if self.value():
			return queryset.filter(organisation_id=self.value())
		return queryset


class StockMovementInline(admin.TabularInline):
	model = StockMovement
	extra = 0
	readonly_fields = ('created_at', 'movement_direction')
	fields = ('movement_type', 'quantity_before', 'quantity_after', 'quantity_change', 'reason', 'created_by', 'created_at')
	
	def has_add_permission(self, request, obj):
		return False  # Disable manual adding through inline

class PriceHistoryInline(admin.TabularInline):
	model = PriceHistory
	extra = 0
	readonly_fields = ('created_at', 'change_percentage')
	fields = ('old_price', 'new_price', 'price_change', 'change_type', 'change_reason', 'updated_by', 'created_at')

class StockAlertInline(admin.TabularInline):
	model = StockAlert
	extra = 0
	readonly_fields = ('created_at',)
	fields = ('alert_type', 'severity', 'message', 'is_read', 'is_resolved', 'created_at')

class StockRecommendationInline(admin.TabularInline):
	model = StockRecommendation
	extra = 0
	readonly_fields = ('created_at',)
	fields = ('recommendation_type', 'suggested_quantity', 'suggested_discount', 'confidence_score', 'is_applied', 'created_at')

@admin.register(ProductsAndStock)
class ProductsAndStockAdmin(admin.ModelAdmin):
	list_display = ('product_name', 'category', 'subcategory', 'product_quantity', 'minimum_stock_level', 'stock_status', 'product_price', 'cost_price', 'profit_margin_percentage', 'organisation')
	list_filter = (OrganisorListFilter, 'category', 'subcategory', 'minimum_stock_level', 'discount_percentage')
	search_fields = ('product_name', 'product_description')
	readonly_fields = ('total_value', 'is_low_stock', 'stock_status', 'profit_margin_amount', 'profit_margin_percentage', 'discounted_price', 'is_discount_active', 'total_sales_today', 'total_revenue_today', 'has_active_alerts', 'critical_alerts_count', 'days_since_last_sale', 'total_sales_count', 'total_revenue_from_sales', 'sales_count_today', 'last_sale_date')
	inlines = [StockMovementInline, PriceHistoryInline, StockAlertInline, StockRecommendationInline]
	
	fieldsets = (
		('Product Information', {
			'fields': ('product_name', 'product_description', 'category', 'subcategory', 'organisation')
		}),
		('Stock Information', {
			'fields': ('product_quantity', 'minimum_stock_level', 'stock_status', 'is_low_stock')
		}),
		('Pricing', {
			'fields': ('product_price', 'cost_price', 'profit_margin_amount', 'profit_margin_percentage', 'total_value')
		}),
		('Sales Information', {
			'fields': ('total_sales_count', 'total_revenue_from_sales', 'sales_count_today', 'last_sale_date'),
			'classes': ('collapse',)
		}),
		('Discount Information', {
			'fields': ('discount_percentage', 'discount_amount', 'discount_start_date', 'discount_end_date', 'discounted_price', 'is_discount_active'),
			'classes': ('collapse',)
		}),
	)
	
	def stock_status(self, obj):
		return obj.stock_status
	stock_status.short_description = 'Stock Status'

@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
	list_display = ('product', 'movement_type', 'quantity_change', 'quantity_before', 'quantity_after', 'reason', 'created_by', 'created_at')
	list_filter = ('movement_type', 'created_at', 'product__organisation')
	search_fields = ('product__product_name', 'reason')
	readonly_fields = ('created_at', 'movement_direction')
	date_hierarchy = 'created_at'
	
	def has_add_permission(self, request):
		return False  # Disable manual adding - movements are created automatically

class SubCategoryInline(admin.TabularInline):
	model = SubCategory
	extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	list_display = ('name', 'description', 'created_at')
	search_fields = ('name', 'description')
	inlines = [SubCategoryInline]
	
	fieldsets = (
		('Category Information', {
			'fields': ('name', 'description', 'icon')
		}),
	)

@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
	list_display = ('name', 'category', 'description', 'created_at')
	list_filter = ('category',)
	search_fields = ('name', 'description')
	
	fieldsets = (
		('Sub Category Information', {
			'fields': ('name', 'category', 'description')
		}),
	)

@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
	list_display = ('product', 'old_price', 'new_price', 'price_change', 'change_type', 'change_percentage', 'updated_by', 'created_at')
	list_filter = ('change_type', 'created_at', 'product__organisation')
	search_fields = ('product__product_name', 'change_reason')
	readonly_fields = ('created_at', 'change_percentage')
	date_hierarchy = 'created_at'
	
	fieldsets = (
		('Price Change Information', {
			'fields': ('product', 'old_price', 'new_price', 'price_change', 'change_percentage')
		}),
		('Change Details', {
			'fields': ('change_type', 'change_reason', 'discount_percentage')
		}),
		('Audit Information', {
			'fields': ('updated_by', 'created_at'),
			'classes': ('collapse',)
		}),
	)
	
	def change_percentage(self, obj):
		return f"{obj.change_percentage:.2f}%"
	change_percentage.short_description = 'Change %'

@admin.register(SalesStatistics)
class SalesStatisticsAdmin(admin.ModelAdmin):
	list_display = ('product', 'date', 'total_sales', 'total_revenue', 'avg_daily_sales', 'last_sale_date')
	list_filter = ('date', 'product__category')
	search_fields = ('product__product_name',)
	readonly_fields = ('date',)
	ordering = ['-date', '-total_sales']

@admin.register(StockAlert)
class StockAlertAdmin(admin.ModelAdmin):
	list_display = ('product', 'alert_type', 'severity', 'is_read', 'is_resolved', 'created_at')
	list_filter = ('alert_type', 'severity', 'is_read', 'is_resolved', 'created_at', 'product__category')
	search_fields = ('product__product_name', 'message')
	readonly_fields = ('created_at',)
	ordering = ['-created_at']
	
	def mark_as_read(self, request, queryset):
		queryset.update(is_read=True)
	mark_as_read.short_description = "Mark selected alerts as read"
	
	def mark_as_resolved(self, request, queryset):
		from django.utils import timezone
		queryset.update(is_resolved=True, resolved_at=timezone.now())
	mark_as_resolved.short_description = "Mark selected alerts as resolved"
	
	actions = [mark_as_read, mark_as_resolved]

@admin.register(StockRecommendation)
class StockRecommendationAdmin(admin.ModelAdmin):
	list_display = ('product', 'recommendation_type', 'confidence_score', 'is_applied', 'created_at')
	list_filter = ('recommendation_type', 'is_applied', 'created_at', 'product__category')
	search_fields = ('product__product_name', 'reason')
	readonly_fields = ('created_at',)
	ordering = ['-confidence_score', '-created_at']
	
	def apply_recommendation(self, request, queryset):
		from django.utils import timezone
		queryset.update(is_applied=True, applied_at=timezone.now())
	apply_recommendation.short_description = "Apply selected recommendations"
	
	actions = [apply_recommendation]
