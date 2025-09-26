# finance/tests.py
from django.test import TestCase, Client
from django.urls import reverse
from finance.models import OrderFinanceReport
from orders.models import orders
from django.utils import timezone
from datetime import datetime

class FinancialReportViewTests(TestCase):
	def setUp(self):
		self.client = Client()
		self.url = reverse('financial_report')  # Adjust the URL name as per your urls.py
		self.order = orders.objects.create(order_name="Test Order", order_day=timezone.now())
		self.report = OrderFinanceReport.objects.create(order=self.order, earned_amount=100.0)

	def test_get_request(self):
		response = self.client.get(self.url)
		self.assertEqual(response.status_code, 200)
		self.assertTemplateUsed(response, 'finance/financial_report.html')
		self.assertIn('form', response.context)
		self.assertIsNone(response.context['total_earned'])
		self.assertEqual(response.context['reports'], [])