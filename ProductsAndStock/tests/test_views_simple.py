"""
ProductsAndStock View Tests - Simplified Version
Basic access control tests only
"""

from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from ProductsAndStock.models import ProductsAndStock, Category, SubCategory
from leads.models import UserProfile, Agent
from organisors.models import Organisor

User = get_user_model()

SIMPLE_STATIC = {'STATICFILES_STORAGE': 'django.contrib.staticfiles.storage.StaticFilesStorage'}


@override_settings(**SIMPLE_STATIC)
class TestProductAndStockViewsSimple(TestCase):
    """Simplified view tests - access control only"""
    
    def setUp(self):
        """Set up test data"""
        # Admin user
        self.admin_user = User.objects.create_user(
            username="admin_simple",
            email="admin_simple@example.com",
            password="adminpass123",
            is_superuser=True
        )
        
        # Organisor user
        self.organisor_user = User.objects.create_user(
            username="organisor_simple",
            email="organisor_simple@example.com",
            password="organisorpass123",
            is_organisor=True
        )
        self.organisor_profile, created = UserProfile.objects.get_or_create(
            user=self.organisor_user
        )
        if created:
            self.organisor_profile.save()
        
        # Create organisor model
        self.organisor = Organisor.objects.create(
            user=self.organisor_user,
            organisation=self.organisor_profile
        )
        
        # Agent user
        self.agent_user = User.objects.create_user(
            username="agent_simple",
            email="agent_simple@example.com",
            password="agentpass123",
            is_agent=True
        )
        self.agent_profile, created = UserProfile.objects.get_or_create(
            user=self.agent_user
        )
        if created:
            self.agent_profile.save()
        
        # Create agent model
        self.agent = Agent.objects.create(
            user=self.agent_user,
            organisation=self.organisor_profile
        )
        
        # Test category
        self.category = Category.objects.create(
            name="Test Category",
            description="Test category description"
        )
        
        # Test subcategory
        self.subcategory = SubCategory.objects.create(
            name="Test SubCategory",
            category=self.category,
            description="Test subcategory description"
        )
        
        # Test product (for organisor)
        self.product = ProductsAndStock.objects.create(
            product_name="Test Product",
            product_price=100.0,
            product_quantity=50,
            category=self.category,
            subcategory=self.subcategory,
            organisation=self.organisor_profile
        )
        
        # Product from same organisation for agent
        self.agent_product = ProductsAndStock.objects.create(
            product_name="Agent Product",
            product_price=200.0,
            product_quantity=30,
            category=self.category,
            subcategory=self.subcategory,
            organisation=self.agent_profile  # Agent's own organisation
        )
        
        self.client = Client()
    
    def test_list_view_admin_access(self):
        """Admin user list view access"""
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('ProductsAndStock:ProductAndStock-list'))
        self.assertEqual(response.status_code, 200)
    
    def test_list_view_organisor_access(self):
        """Organisor user list view access"""
        self.client.force_login(self.organisor_user)
        response = self.client.get(reverse('ProductsAndStock:ProductAndStock-list'))
        self.assertEqual(response.status_code, 200)
    
    def test_list_view_agent_access(self):
        """Agent user list view access"""
        self.client.force_login(self.agent_user)
        response = self.client.get(reverse('ProductsAndStock:ProductAndStock-list'))
        self.assertEqual(response.status_code, 200)
    
    def test_list_view_anonymous_redirect(self):
        """Anonymous user redirect"""
        response = self.client.get(reverse('ProductsAndStock:ProductAndStock-list'))
        self.assertEqual(response.status_code, 302)
    
    def test_detail_view_admin_access(self):
        """Admin user detail view access"""
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('ProductsAndStock:ProductAndStock-detail', kwargs={'pk': self.product.pk}))
        self.assertEqual(response.status_code, 200)
    
    def test_detail_view_organisor_access(self):
        """Organisor user detail view access"""
        self.client.force_login(self.organisor_user)
        response = self.client.get(reverse('ProductsAndStock:ProductAndStock-detail', kwargs={'pk': self.product.pk}))
        self.assertEqual(response.status_code, 200)
    
    def test_detail_view_agent_access(self):
        """Agent user detail view access"""
        self.client.force_login(self.agent_user)
        response = self.client.get(reverse('ProductsAndStock:ProductAndStock-detail', kwargs={'pk': self.agent_product.pk}))
        self.assertEqual(response.status_code, 200)
    
    def test_create_view_admin_access(self):
        """Admin user create view access"""
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('ProductsAndStock:ProductAndStock-create'))
        self.assertEqual(response.status_code, 200)
    
    def test_create_view_organisor_access(self):
        """Organisor user create view access"""
        self.client.force_login(self.organisor_user)
        response = self.client.get(reverse('ProductsAndStock:ProductAndStock-create'))
        self.assertEqual(response.status_code, 200)
    
    def test_create_view_agent_access(self):
        """Agent user create view access"""
        self.client.force_login(self.agent_user)
        response = self.client.get(reverse('ProductsAndStock:ProductAndStock-create'))
        self.assertEqual(response.status_code, 200)
    
    def test_update_view_admin_access(self):
        """Admin user update view access"""
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('ProductsAndStock:ProductAndStock-update', kwargs={'pk': self.product.pk}))
        self.assertEqual(response.status_code, 200)
    
    def test_update_view_organisor_access(self):
        """Organisor user update view access"""
        self.client.force_login(self.organisor_user)
        response = self.client.get(reverse('ProductsAndStock:ProductAndStock-update', kwargs={'pk': self.product.pk}))
        self.assertEqual(response.status_code, 200)
    
    def test_update_view_agent_access(self):
        """Agent user update view access"""
        self.client.force_login(self.agent_user)
        response = self.client.get(reverse('ProductsAndStock:ProductAndStock-update', kwargs={'pk': self.agent_product.pk}))
        self.assertEqual(response.status_code, 200)
    
    def test_delete_view_admin_access(self):
        """Admin user delete view access"""
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('ProductsAndStock:ProductAndStock-delete', kwargs={'pk': self.product.pk}))
        self.assertEqual(response.status_code, 200)
    
    def test_delete_view_organisor_access(self):
        """Organisor user delete view access"""
        self.client.force_login(self.organisor_user)
        response = self.client.get(reverse('ProductsAndStock:ProductAndStock-delete', kwargs={'pk': self.product.pk}))
        self.assertEqual(response.status_code, 200)
    
    def test_delete_view_agent_access(self):
        """Agent user delete view access"""
        self.client.force_login(self.agent_user)
        response = self.client.get(reverse('ProductsAndStock:ProductAndStock-delete', kwargs={'pk': self.agent_product.pk}))
        self.assertEqual(response.status_code, 200)
    
    def test_sales_dashboard_admin_access(self):
        """Admin user sales dashboard access"""
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('ProductsAndStock:sales-dashboard'))
        self.assertEqual(response.status_code, 200)
    
    def test_sales_dashboard_organisor_access(self):
        """Organisor user sales dashboard access"""
        self.client.force_login(self.organisor_user)
        response = self.client.get(reverse('ProductsAndStock:sales-dashboard'))
        self.assertEqual(response.status_code, 200)
    
    def test_sales_dashboard_agent_access(self):
        """Agent user sales dashboard access"""
        self.client.force_login(self.agent_user)
        response = self.client.get(reverse('ProductsAndStock:sales-dashboard'))
        self.assertEqual(response.status_code, 200)
