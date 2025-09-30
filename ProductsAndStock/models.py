from django.db import models
from django.db.models.signals import post_save
from leads.models import User, UserProfile  # Import User and UserProfile from leads app

class ProductsAndStock(models.Model):
	product_name = models.CharField(max_length=20)
	product_description = models.TextField()
	product_price = models.FloatField()
	product_quantity = models.IntegerField()
	organisation = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

	class Meta:
		unique_together = ('product_name', 'organisation')

	def __str__(self):
		return self.product_name


