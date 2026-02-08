from django.db import models
from django.db.models.signals import post_save, pre_save
from django.core.mail import send_mail
from django.conf import settings
from leads.models import User, UserProfile  # Import User and UserProfile from leads app

class Category(models.Model):
	name = models.CharField(max_length=50, unique=True)
	description = models.TextField(blank=True, null=True)
	icon = models.CharField(max_length=50, blank=True, null=True, help_text="Font Awesome icon class (e.g., 'fas fa-mobile-alt')")
	created_at = models.DateTimeField(auto_now_add=True)
	
	class Meta:
		verbose_name = "Category"
		verbose_name_plural = "Categories"
		ordering = ['name']
	
	def __str__(self):
		return self.name

class SubCategory(models.Model):
	name = models.CharField(max_length=50)
	category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
	description = models.TextField(blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	
	class Meta:
		verbose_name = "Sub Category"
		verbose_name_plural = "Sub Categories"
		ordering = ['category', 'name']
		unique_together = ('name', 'category')
	
	def __str__(self):
		return f"{self.category.name} - {self.name}"


class ProductsAndStock(models.Model):
	product_name = models.CharField(max_length=20)
	product_description = models.TextField()
	product_price = models.FloatField(verbose_name="Selling Price")
	cost_price = models.FloatField(default=0.0, verbose_name="Cost Price", help_text="Purchase/production cost")
	product_quantity = models.IntegerField()
	minimum_stock_level = models.IntegerField(default=0, help_text="Minimum stock level for alerts")
	category = models.ForeignKey(Category, on_delete=models.CASCADE, null=False, blank=False, default=1)
	subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, null=False, blank=False, default=1)
	organisation = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
	
	# Discount fields
	discount_percentage = models.FloatField(default=0.0, help_text="Discount percentage (0-100)")
	discount_amount = models.FloatField(default=0.0, help_text="Fixed discount amount")
	discount_start_date = models.DateTimeField(null=True, blank=True)
	discount_end_date = models.DateTimeField(null=True, blank=True)

	class Meta:
		unique_together = ('product_name', 'organisation')

	def __str__(self):
		return self.product_name
	
	def clean(self):
		from django.core.exceptions import ValidationError
		
		# Validate that subcategory belongs to the selected category
		if self.category and self.subcategory:
			if self.subcategory.category != self.category:
				raise ValidationError(
					f"Subcategory '{self.subcategory.name}' does not belong to category '{self.category.name}'"
				)

	@property
	def total_value(self):
		"""Calculate total value of the product (price * quantity)"""
		return self.product_price * self.product_quantity
	
	@property
	def is_low_stock(self):
		"""Check if stock is below minimum level"""
		return self.product_quantity <= self.minimum_stock_level
	
	@property
	def stock_status(self):
		"""Get stock status as string: Out of Stock, Low Stock, Overstock, In Stock"""
		if self.product_quantity <= 0:
			return "Out of Stock"
		if self.is_low_stock:
			return "Low Stock"
		if self.minimum_stock_level and self.product_quantity > self.minimum_stock_level * 10:
			return "Overstock"
		return "In Stock"
	
	@property
	def profit_margin_amount(self):
		"""Calculate profit margin amount (selling price - cost price)"""
		return self.product_price - self.cost_price
	
	@property
	def profit_margin_percentage(self):
		"""Calculate profit margin percentage"""
		if self.cost_price > 0:
			return (self.profit_margin_amount / self.cost_price) * 100
		return 0
	
	@property
	def discounted_price(self):
		"""Calculate final price after discount"""
		from django.utils import timezone
		
		# Check if discount is active
		is_discount_active = True
		if self.discount_start_date and self.discount_end_date:
			now = timezone.now()
			is_discount_active = self.discount_start_date <= now <= self.discount_end_date
		
		if not is_discount_active:
			return self.product_price
		
		# Apply percentage discount
		if self.discount_percentage > 0:
			discount_amount = self.product_price * (self.discount_percentage / 100)
			final_price = self.product_price - discount_amount
		else:
			final_price = self.product_price
		
		# Apply fixed discount
		if self.discount_amount > 0:
			final_price = final_price - self.discount_amount
		
		return max(0, final_price)  # Ensure price doesn't go below 0
	
	@property
	def is_discount_active(self):
		"""Check if discount is currently active"""
		from django.utils import timezone
		
		if not (self.discount_percentage > 0 or self.discount_amount > 0):
			return False
		
		if self.discount_start_date and self.discount_end_date:
			now = timezone.now()
			return self.discount_start_date <= now <= self.discount_end_date
		
		return True  # If no date restrictions, discount is always active
	
	@property
	def total_profit(self):
		"""Calculate total profit (profit margin amount * quantity)"""
		return self.profit_margin_amount * self.product_quantity
	
	@property
	def total_sales_today(self):
		"""Get total sales for today"""
		from django.utils import timezone
		today = timezone.now().date()
		try:
			today_stats = self.sales_stats.get(date=today)
			return today_stats.total_sales
		except:
			return 0
	
	@property
	def total_revenue_today(self):
		"""Get total revenue for today"""
		from django.utils import timezone
		today = timezone.now().date()
		try:
			today_stats = self.sales_stats.get(date=today)
			return today_stats.total_revenue
		except:
			return 0
	
	@property
	def has_active_alerts(self):
		"""Check if product has active (unresolved) alerts"""
		return self.stock_alerts.filter(is_resolved=False).exists()
	
	@property
	def critical_alerts_count(self):
		"""Count of critical unresolved alerts"""
		return self.stock_alerts.filter(is_resolved=False, severity='CRITICAL').count()
	
	@property
	def worst_active_alert_severity(self):
		"""Highest severity among unresolved alerts (CRITICAL > HIGH > MEDIUM > LOW), or None."""
		severity_order = {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
		severities = list(
			self.stock_alerts.filter(is_resolved=False).values_list('severity', flat=True)
		)
		if not severities:
			return None
		return max(severities, key=lambda s: severity_order.get(s, 0))
	
	@property
	def days_since_last_sale(self):
		"""Calculate days since last sale"""
		from django.utils import timezone
		try:
			latest_stats = self.sales_stats.filter(total_sales__gt=0).first()
			if latest_stats and latest_stats.last_sale_date:
				delta = timezone.now() - latest_stats.last_sale_date
				return delta.days
			return None
		except:
			return None
	
	@property
	def total_sales_count(self):
		"""Get total number of sales (from orders)"""
		from orders.models import OrderProduct
		try:
			total_sold = OrderProduct.objects.filter(
				product=self,
				order__is_cancelled=False
			).aggregate(
				total=models.Sum('product_quantity')
			)['total']
			return total_sold if total_sold else 0
		except:
			return 0
	
	@property
	def total_revenue_from_sales(self):
		"""Get total revenue from actual sales"""
		from orders.models import OrderProduct
		try:
			total_revenue = OrderProduct.objects.filter(
				product=self,
				order__is_cancelled=False
			).aggregate(
				total=models.Sum('total_price')
			)['total']
			return total_revenue if total_revenue else 0
		except:
			return 0
	
	@property
	def sales_count_today(self):
		"""Get sales count for today"""
		from orders.models import OrderProduct
		from django.utils import timezone
		today = timezone.now().date()
		try:
			today_sales = OrderProduct.objects.filter(
				product=self,
				order__is_cancelled=False,
				order__creation_date__date=today
			).aggregate(
				total=models.Sum('product_quantity')
			)['total']
			return today_sales if today_sales else 0
		except:
			return 0
	
	@property
	def last_sale_date(self):
		"""Get date of last sale"""
		from orders.models import OrderProduct
		try:
			last_order = OrderProduct.objects.filter(
				product=self,
				order__is_cancelled=False
			).order_by('-order__creation_date').first()
			return last_order.order.creation_date if last_order else None
		except:
			return None
	
	def send_low_stock_alert(self):
		"""Send email alert when stock is low"""
		if self.is_low_stock and self.organisation.user.email:
			subject = f'🚨 CRITICAL STOCK ALERT - {self.product_name}'
			message = f"""
Hello {self.organisation.user.first_name},

Your {self.product_name} product stock level is critical!

📊 Stock Information:
• Product Name: {self.product_name}
• Current Stock: {self.product_quantity}
• Minimum Stock Level: {self.minimum_stock_level}
• Stock Status: {self.stock_status}

⚠️ Urgent stock replenishment is recommended.

This message was sent automatically.
Darkenyas CRM System
			"""
			
			try:
				send_mail(
					subject,
					message,
					settings.DEFAULT_FROM_EMAIL,
					[self.organisation.user.email],
					fail_silently=False,
				)
				print(f"Low stock alert sent for {self.product_name} to {self.organisation.user.email}")
			except Exception as e:
				print(f"Failed to send low stock alert: {e}")

def check_stock_level(sender, instance, **kwargs):
	"""Signal to check stock level after save"""
	# Only check if this is an update (not creation)
	if instance.pk:
		# Check if stock is now low
		if instance.is_low_stock:
			instance.send_low_stock_alert()

# Connect the signal
post_save.connect(check_stock_level, sender=ProductsAndStock)

# Store previous data for tracking
_previous_data = {}

def store_previous_data(sender, instance, **kwargs):
	"""Store the previous data before save"""
	if instance.pk:
		try:
			old_instance = ProductsAndStock.objects.get(pk=instance.pk)
			_previous_data[instance.pk] = {
				'product_quantity': old_instance.product_quantity,
				'product_price': old_instance.product_price,
			}
		except ProductsAndStock.DoesNotExist:
			pass

def create_stock_movement(sender, instance, created, **kwargs):
	"""Create stock movement record after save. Skip when order already created one (avoid duplicate)."""
	if not created:
		# OrderProduct.reduce_stock/restore_stock create their own StockMovement; skip duplicate
		if getattr(instance, '_skip_stock_movement_signal', False):
			if instance.pk in _previous_data:
				del _previous_data[instance.pk]
			return
	if created:
		# For new products, create initial stock movement
		StockMovement.objects.create(
			product=instance,
			movement_type='IN',
			quantity_before=0,
			quantity_after=instance.product_quantity,
			quantity_change=instance.product_quantity,
			reason='Initial stock',
			created_by=getattr(instance, '_current_user', None)
		)
	else:
		# For updates, check if quantity changed
		previous_data = _previous_data.get(instance.pk, {})
		previous_quantity = previous_data.get('product_quantity', 0)
		
		if previous_quantity != instance.product_quantity:
			quantity_change = instance.product_quantity - previous_quantity
			
			# Determine movement type
			if quantity_change > 0:
				movement_type = 'IN'
				reason = 'Stock replenishment'
			elif quantity_change < 0:
				movement_type = 'OUT'
				reason = 'Stock reduction'
			else:
				movement_type = 'ADJUSTMENT'
				reason = 'Stock adjustment'
			
			# Create stock movement record
			StockMovement.objects.create(
				product=instance,
				movement_type=movement_type,
				quantity_before=previous_quantity,
				quantity_after=instance.product_quantity,
				quantity_change=quantity_change,
				reason=reason,
				created_by=getattr(instance, '_current_user', None)
			)

def create_price_history(sender, instance, created, **kwargs):
	"""Create price history record after save (skip if bulk update will add its own)"""
	if not created:  # Only for updates, not new products
		# Bulk Price Update view creates its own PriceHistory with custom reason; don't duplicate
		if getattr(instance, '_skip_price_history_signal', False):
			if instance.pk in _previous_data:
				del _previous_data[instance.pk]
			return
		previous_data = _previous_data.get(instance.pk, {})
		previous_price = previous_data.get('product_price', 0)
		
		if previous_price != instance.product_price:
			price_change = instance.product_price - previous_price
			
			# Determine change type
			if price_change > 0:
				change_type = 'INCREASE'
			elif price_change < 0:
				change_type = 'DECREASE'
			else:
				change_type = 'MANUAL'
			
			# Create price history record
			PriceHistory.objects.create(
				product=instance,
				old_price=previous_price,
				new_price=instance.product_price,
				price_change=price_change,
				change_type=change_type,
				change_reason=f'Price updated from {previous_price:.2f} to {instance.product_price:.2f}',
				updated_by=getattr(instance, '_current_user', None)
			)
		
		# Clean up stored data
		if instance.pk in _previous_data:
			del _previous_data[instance.pk]

def create_stock_alerts(sender, instance, created, **kwargs):
	"""Create stock alerts based on stock levels"""
	# Low stock alert
	if instance.is_low_stock and instance.product_quantity > 0:
		severity = 'CRITICAL' if instance.product_quantity <= instance.minimum_stock_level / 2 else 'HIGH'
		StockAlert.objects.create(
			product=instance,
			alert_type='LOW_STOCK',
			severity=severity,
			message=f'Stock level is low: {instance.product_quantity} units remaining (minimum: {instance.minimum_stock_level})'
		)
	
	# Out of stock alert
	if instance.product_quantity <= 0:
		StockAlert.objects.create(
			product=instance,
			alert_type='OUT_OF_STOCK',
			severity='CRITICAL',
			message='Product is out of stock!'
		)
	
	# Overstock alert (if stock is too high)
	if instance.product_quantity > instance.minimum_stock_level * 10:
		StockAlert.objects.create(
			product=instance,
			alert_type='OVERSTOCK',
			severity='MEDIUM',
			message=f'Stock level is very high: {instance.product_quantity} units (consider reducing stock)'
		)

def create_stock_recommendations(sender, instance, created, **kwargs):
	"""Create stock recommendations based on various factors"""
	# Restock recommendation for low stock
	if instance.is_low_stock:
		suggested_quantity = instance.minimum_stock_level * 3
		StockRecommendation.objects.create(
			product=instance,
			recommendation_type='RESTOCK',
			suggested_quantity=suggested_quantity,
			reason=f'Low stock level. Recommended to restock to {suggested_quantity} units.',
			confidence_score=85.0
		)
	
	# Discount recommendation for overstock
	if instance.product_quantity > instance.minimum_stock_level * 5:
		suggested_discount = 15.0
		StockRecommendation.objects.create(
			product=instance,
			recommendation_type='DISCOUNT',
			suggested_discount=suggested_discount,
			reason=f'High stock level. Consider offering {suggested_discount}% discount to increase sales.',
			confidence_score=70.0
		)
	
	# Reduce stock recommendation for very high stock
	if instance.product_quantity > instance.minimum_stock_level * 10:
		StockRecommendation.objects.create(
			product=instance,
			recommendation_type='REDUCE_STOCK',
			suggested_quantity=instance.minimum_stock_level * 2,
			reason=f'Very high stock level. Consider reducing stock to {instance.minimum_stock_level * 2} units.',
			confidence_score=80.0
		)

# Connect the signals
pre_save.connect(store_previous_data, sender=ProductsAndStock)
post_save.connect(create_stock_movement, sender=ProductsAndStock)
post_save.connect(create_price_history, sender=ProductsAndStock)
post_save.connect(create_stock_alerts, sender=ProductsAndStock)
post_save.connect(create_stock_recommendations, sender=ProductsAndStock)

class StockMovement(models.Model):
	MOVEMENT_TYPES = [
		('IN', 'Stock In'),
		('OUT', 'Stock Out'),
		('ADJUSTMENT', 'Stock Adjustment'),
		('UPDATE', 'Stock Update'),
	]
	
	product = models.ForeignKey(ProductsAndStock, on_delete=models.CASCADE, related_name='stock_movements')
	movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
	quantity_before = models.IntegerField()
	quantity_after = models.IntegerField()
	quantity_change = models.IntegerField()  # Positive for IN, negative for OUT
	reason = models.CharField(max_length=255, blank=True, null=True)
	created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	
	class Meta:
		ordering = ['-created_at']
		verbose_name = "Stock Movement"
		verbose_name_plural = "Stock Movements"
	
	def __str__(self):
		return f"{self.product.product_name} - {self.get_movement_type_display()} ({self.quantity_change:+d})"
	
	@property
	def movement_direction(self):
		"""Get movement direction as string"""
		if self.quantity_change > 0:
			return "IN"
		elif self.quantity_change < 0:
			return "OUT"
		else:
			return "NO CHANGE"

class PriceHistory(models.Model):
	CHANGE_TYPES = [
		('INCREASE', 'Price Increase'),
		('DECREASE', 'Price Decrease'),
		('DISCOUNT', 'Discount Applied'),
		('BULK_UPDATE', 'Bulk Price Update'),
		('MANUAL', 'Manual Update'),
	]
	
	product = models.ForeignKey(ProductsAndStock, on_delete=models.CASCADE, related_name='price_history')
	old_price = models.FloatField()
	new_price = models.FloatField()
	price_change = models.FloatField()  # Positive for increase, negative for decrease
	change_type = models.CharField(max_length=20, choices=CHANGE_TYPES)
	change_reason = models.CharField(max_length=255, blank=True, null=True)
	discount_percentage = models.FloatField(null=True, blank=True, help_text="Discount percentage if applicable")
	updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	
	class Meta:
		verbose_name = "Price History"
		verbose_name_plural = "Price Histories"
		ordering = ['-created_at']
	
	def __str__(self):
		return f"{self.product.product_name} - {self.get_change_type_display()} ({self.price_change:+.2f})"
	
	@property
	def change_percentage(self):
		"""Calculate percentage change"""
		if self.old_price > 0:
			return (self.price_change / self.old_price) * 100
		return 0

class SalesStatistics(models.Model):
	"""Model to track sales statistics for products"""
	product = models.ForeignKey(ProductsAndStock, on_delete=models.CASCADE, related_name='sales_stats')
	date = models.DateField(auto_now_add=True)
	total_sales = models.IntegerField(default=0, help_text="Total quantity sold today")
	total_revenue = models.FloatField(default=0.0, help_text="Total revenue from sales today")
	avg_daily_sales = models.FloatField(default=0.0, help_text="Average daily sales (last 30 days)")
	last_sale_date = models.DateTimeField(null=True, blank=True)
	
	class Meta:
		verbose_name = "Sales Statistics"
		verbose_name_plural = "Sales Statistics"
		ordering = ['-total_sales']
		unique_together = ('product', 'date')
	
	def __str__(self):
		return f"{self.product.product_name} - {self.date} ({self.total_sales} sales)"

class StockAlert(models.Model):
	ALERT_TYPES = [
		('LOW_STOCK', 'Low Stock Alert'),
		('OUT_OF_STOCK', 'Out of Stock Alert'),
		('OVERSTOCK', 'Overstock Alert'),
		('NO_SALES', 'No Sales Alert'),
	]
	
	SEVERITY_LEVELS = [
		('LOW', 'Low'),
		('MEDIUM', 'Medium'),
		('HIGH', 'High'),
		('CRITICAL', 'Critical'),
	]
	
	product = models.ForeignKey(ProductsAndStock, on_delete=models.CASCADE, related_name='stock_alerts')
	alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
	severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS)
	message = models.TextField()
	is_read = models.BooleanField(default=False)
	is_resolved = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	resolved_at = models.DateTimeField(null=True, blank=True)
	
	class Meta:
		verbose_name = "Stock Alert"
		verbose_name_plural = "Stock Alerts"
		ordering = ['-created_at']
	
	def __str__(self):
		return f"{self.product.product_name} - {self.get_alert_type_display()} ({self.severity})"

class StockRecommendation(models.Model):
	RECOMMENDATION_TYPES = [
		('RESTOCK', 'Restock Recommendation'),
		('REDUCE_STOCK', 'Reduce Stock Recommendation'),
		('DISCOUNT', 'Discount Recommendation'),
		('DISCONTINUE', 'Discontinue Recommendation'),
	]
	
	product = models.ForeignKey(ProductsAndStock, on_delete=models.CASCADE, related_name='stock_recommendations')
	recommendation_type = models.CharField(max_length=20, choices=RECOMMENDATION_TYPES)
	suggested_quantity = models.IntegerField(null=True, blank=True, help_text="Suggested stock quantity")
	suggested_discount = models.FloatField(null=True, blank=True, help_text="Suggested discount percentage")
	reason = models.TextField()
	confidence_score = models.FloatField(default=0.0, help_text="Confidence score (0-100)")
	is_applied = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	applied_at = models.DateTimeField(null=True, blank=True)
	
	class Meta:
		verbose_name = "Stock Recommendation"
		verbose_name_plural = "Stock Recommendations"
		ordering = ['-confidence_score', '-created_at']
	
	def __str__(self):
		return f"{self.product.product_name} - {self.get_recommendation_type_display()}"


