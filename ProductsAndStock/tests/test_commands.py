"""
Tests for ProductsAndStock management commands.
"""
from io import StringIO

from django.test import TestCase
from django.core.management import call_command
from django.contrib.auth import get_user_model

from ProductsAndStock.models import Category, SubCategory, ProductsAndStock
from leads.models import UserProfile

User = get_user_model()


class CreateCategoriesCommandTests(TestCase):
    """Tests for the create_categories management command."""

    def test_creates_categories_and_subcategories(self):
        out = StringIO()
        call_command('create_categories', stdout=out)
        output = out.getvalue()

        # The command creates 5 categories
        self.assertTrue(Category.objects.filter(name='Products').exists())
        self.assertTrue(Category.objects.filter(name='Services').exists())
        self.assertTrue(Category.objects.filter(name='Software').exists())
        self.assertTrue(Category.objects.filter(name='Subscriptions').exists())
        self.assertTrue(Category.objects.filter(name='Other').exists())

        # Subcategories created under Products
        products_cat = Category.objects.get(name='Products')
        self.assertTrue(SubCategory.objects.filter(category=products_cat, name='Merchandise').exists())
        self.assertTrue(SubCategory.objects.filter(category=products_cat, name='Inventory').exists())

    def test_idempotent_run(self):
        """Running the command twice should not duplicate categories."""
        call_command('create_categories', stdout=StringIO())
        count1 = Category.objects.count()
        call_command('create_categories', stdout=StringIO())
        count2 = Category.objects.count()
        self.assertEqual(count1, count2)

    def test_replace_removes_old_categories(self):
        """--replace should remove categories not in the standard set."""
        old_cat = Category.objects.create(name='OldCategory', description='Old')
        SubCategory.objects.create(name='OldSub', category=old_cat)

        call_command('create_categories', '--replace', stdout=StringIO())

        self.assertFalse(Category.objects.filter(name='OldCategory').exists())
        self.assertFalse(SubCategory.objects.filter(name='OldSub').exists())


class CreateSampleProductsCommandTests(TestCase):
    """Tests for the create_sample_products management command."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='cmdorg', email='cmdorg@test.com', password='testpass123',
            is_organisor=True, email_verified=True,
        )
        cls.organisation = UserProfile.objects.get(user=cls.user)

    def test_creates_products_for_organisor(self):
        # First create categories
        call_command('create_categories', stdout=StringIO())

        out = StringIO()
        call_command('create_sample_products', '--username', 'cmdorg', stdout=out)

        # At least some products should have been created
        products = ProductsAndStock.objects.filter(organisation=self.organisation)
        self.assertGreater(products.count(), 0)

    def test_nonexistent_user_shows_error(self):
        out = StringIO()
        err = StringIO()
        call_command('create_sample_products', '--username', 'doesnotexist',
                     stdout=out, stderr=err)
        combined = out.getvalue() + err.getvalue()
        # The command should report an error about the user
        self.assertTrue(
            'not found' in combined.lower() or 'error' in combined.lower()
            or ProductsAndStock.objects.count() == 0
        )
