from django.core.management.base import BaseCommand
from leads.models import UserProfile, SourceCategory, ValueCategory

class Command(BaseCommand):
    help = 'Create default source and value categories for all organizations'

    def handle(self, *args, **options):
        # Source-based categories
        source_categories = [
            "Website",
            "Social Media", 
            "Email Campaign",
            "Cold Call",
            "Referral",
            "Trade Show",
            "Advertisement",
            "Direct Mail",
            "SEO/Google",
            "Unassigned"
        ]
        
        # Value-based categories
        value_categories = [
            "Enterprise",      # Large companies
            "SMB",            # Mid-size businesses
            "Small Business", # Small businesses
            "Individual",     # Individual customers
            "High Value",     # High value
            "Medium Value",   # Medium value
            "Low Value",      # Low value
            "Unassigned"
        ]
        
        # Create categories for all organizations
        for organisation in UserProfile.objects.all():
            self.stdout.write(f'Creating categories for {organisation.user.username}...')
            
            # Create source categories
            for category_name in source_categories:
                source_cat, created = SourceCategory.objects.get_or_create(
                    name=category_name,
                    organisation=organisation
                )
                if created:
                    self.stdout.write(f'  Created source category: {category_name}')
            
            # Create value categories
            for category_name in value_categories:
                value_cat, created = ValueCategory.objects.get_or_create(
                    name=category_name,
                    organisation=organisation
                )
                if created:
                    self.stdout.write(f'  Created value category: {category_name}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created default categories for all organizations!')
        )
