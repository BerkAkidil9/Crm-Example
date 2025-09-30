from django.db import models
from django.db.models.signals import post_save
from django.core.mail import send_mail
from django.conf import settings
from leads.models import User, UserProfile  # Import User and UserProfile from leads app

class ProductsAndStock(models.Model):
	product_name = models.CharField(max_length=20)
	product_description = models.TextField()
	product_price = models.FloatField()
	product_quantity = models.IntegerField()
	minimum_stock_level = models.IntegerField(default=0, help_text="Minimum stock level for alerts")
	organisation = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

	class Meta:
		unique_together = ('product_name', 'organisation')

	def __str__(self):
		return self.product_name

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
		"""Get stock status as string"""
		if self.product_quantity <= 0:
			return "Out of Stock"
		elif self.is_low_stock:
			return "Low Stock"
		else:
			return "In Stock"
	
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
DJCrm System
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


