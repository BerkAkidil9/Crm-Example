# finance/models.py
from django.db import models
from django.utils import timezone
from orders.models import orders  # Adjust import based on your project structure

class OrderFinanceReport(models.Model):
    order = models.OneToOneField(orders, on_delete=models.CASCADE)
    earned_amount = models.FloatField()
    report_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Report for {self.order.order_name} - {self.report_date.strftime('%Y-%m-%d')}"

