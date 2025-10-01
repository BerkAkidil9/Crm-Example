"""
ProductsAndStock View Testleri - Basitleştirilmiş Versiyon
Sadece temel access control testleri
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from ProductsAndStock.models import ProductsAndStock, Category, SubCategory
from leads.models import UserProfile

User = get_user_model()


class TestProductAndStockViewsSimple(TestCase):
    """Basitleştirilmiş view testleri - sadece access control"""
    
    def setUp(self):
        """Test verilerini hazırla"""
        # Admin kullanıcı
        self.admin_user = User.objects.create_user(
            username="admin_simple",
            email="admin_simple@example.com",
            password="adminpass123",
            is_superuser=True
        )
        
        # Organisor kullanıcı
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
        
        # Agent kullanıcı
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
        
        # Test kategorisi
        self.category = Category.objects.create(
            name="Test Category",
            description="Test category description"
        )
        
        # Test alt kategorisi
        self.subcategory = SubCategory.objects.create(
            name="Test SubCategory",
            category=self.category,
            description="Test subcategory description"
        )
        
        # Test ürünü (organisor için)
        self.product = ProductsAndStock.objects.create(
            product_name="Test Product",
            product_price=100.0,
            product_quantity=50,
            category=self.category,
            subcategory=self.subcategory,
            organisation=self.organisor_profile
        )
        
        # Agent için aynı organisation'dan ürün
        self.agent_product = ProductsAndStock.objects.create(
            product_name="Agent Product",
            product_price=200.0,
            product_quantity=30,
            category=self.category,
            subcategory=self.subcategory,
            organisation=self.agent_profile  # Agent'ın kendi organisation'ı
        )
        
        self.client = Client()
    
    def test_list_view_admin_access(self):
        """Admin kullanıcı list view erişimi"""
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('ProductsAndStock:ProductAndStock-list'))
        self.assertEqual(response.status_code, 200)
    
    def test_list_view_organisor_access(self):
        """Organisor kullanıcı list view erişimi"""
        self.client.force_login(self.organisor_user)
        response = self.client.get(reverse('ProductsAndStock:ProductAndStock-list'))
        self.assertEqual(response.status_code, 200)
    
    def test_list_view_agent_access(self):
        """Agent kullanıcı list view erişimi"""
        self.client.force_login(self.agent_user)
        response = self.client.get(reverse('ProductsAndStock:ProductAndStock-list'))
        self.assertEqual(response.status_code, 200)
    
    def test_list_view_anonymous_redirect(self):
        """Anonim kullanıcı redirect"""
        response = self.client.get(reverse('ProductsAndStock:ProductAndStock-list'))
        self.assertEqual(response.status_code, 302)
    
    def test_detail_view_admin_access(self):
        """Admin kullanıcı detail view erişimi"""
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('ProductsAndStock:ProductAndStock-detail', kwargs={'pk': self.product.pk}))
        self.assertEqual(response.status_code, 200)
    
    def test_detail_view_organisor_access(self):
        """Organisor kullanıcı detail view erişimi"""
        self.client.force_login(self.organisor_user)
        response = self.client.get(reverse('ProductsAndStock:ProductAndStock-detail', kwargs={'pk': self.product.pk}))
        self.assertEqual(response.status_code, 200)
    
    def test_detail_view_agent_access(self):
        """Agent kullanıcı detail view erişimi"""
        self.client.force_login(self.agent_user)
        response = self.client.get(reverse('ProductsAndStock:ProductAndStock-detail', kwargs={'pk': self.agent_product.pk}))
        self.assertEqual(response.status_code, 200)
    
    def test_create_view_admin_access(self):
        """Admin kullanıcı create view erişimi"""
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('ProductsAndStock:ProductAndStock-create'))
        self.assertEqual(response.status_code, 200)
    
    def test_create_view_organisor_access(self):
        """Organisor kullanıcı create view erişimi"""
        self.client.force_login(self.organisor_user)
        response = self.client.get(reverse('ProductsAndStock:ProductAndStock-create'))
        self.assertEqual(response.status_code, 200)
    
    def test_create_view_agent_access(self):
        """Agent kullanıcı create view erişimi"""
        self.client.force_login(self.agent_user)
        response = self.client.get(reverse('ProductsAndStock:ProductAndStock-create'))
        self.assertEqual(response.status_code, 200)
    
    def test_update_view_admin_access(self):
        """Admin kullanıcı update view erişimi"""
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('ProductsAndStock:ProductAndStock-update', kwargs={'pk': self.product.pk}))
        self.assertEqual(response.status_code, 200)
    
    def test_update_view_organisor_access(self):
        """Organisor kullanıcı update view erişimi"""
        self.client.force_login(self.organisor_user)
        response = self.client.get(reverse('ProductsAndStock:ProductAndStock-update', kwargs={'pk': self.product.pk}))
        self.assertEqual(response.status_code, 200)
    
    def test_update_view_agent_access(self):
        """Agent kullanıcı update view erişimi"""
        self.client.force_login(self.agent_user)
        response = self.client.get(reverse('ProductsAndStock:ProductAndStock-update', kwargs={'pk': self.agent_product.pk}))
        self.assertEqual(response.status_code, 200)
    
    def test_delete_view_admin_access(self):
        """Admin kullanıcı delete view erişimi"""
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('ProductsAndStock:ProductAndStock-delete', kwargs={'pk': self.product.pk}))
        self.assertEqual(response.status_code, 200)
    
    def test_delete_view_organisor_access(self):
        """Organisor kullanıcı delete view erişimi"""
        self.client.force_login(self.organisor_user)
        response = self.client.get(reverse('ProductsAndStock:ProductAndStock-delete', kwargs={'pk': self.product.pk}))
        self.assertEqual(response.status_code, 200)
    
    def test_delete_view_agent_access(self):
        """Agent kullanıcı delete view erişimi"""
        self.client.force_login(self.agent_user)
        response = self.client.get(reverse('ProductsAndStock:ProductAndStock-delete', kwargs={'pk': self.agent_product.pk}))
        self.assertEqual(response.status_code, 200)
    
    def test_sales_dashboard_admin_access(self):
        """Admin kullanıcı sales dashboard erişimi"""
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('ProductsAndStock:sales-dashboard'))
        self.assertEqual(response.status_code, 200)
    
    def test_sales_dashboard_organisor_access(self):
        """Organisor kullanıcı sales dashboard erişimi"""
        self.client.force_login(self.organisor_user)
        response = self.client.get(reverse('ProductsAndStock:sales-dashboard'))
        self.assertEqual(response.status_code, 200)
    
    def test_sales_dashboard_agent_access(self):
        """Agent kullanıcı sales dashboard erişimi"""
        self.client.force_login(self.agent_user)
        response = self.client.get(reverse('ProductsAndStock:sales-dashboard'))
        self.assertEqual(response.status_code, 200)
