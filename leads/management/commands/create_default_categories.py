from django.core.management.base import BaseCommand
from leads.models import UserProfile, SourceCategory, ValueCategory

class Command(BaseCommand):
    help = 'Create default source and value categories for all organizations'

    def handle(self, *args, **options):
        # Kaynak bazlı kategoriler
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
        
        # Değer bazlı kategoriler
        value_categories = [
            "Enterprise",      # Büyük şirketler
            "SMB",            # Orta ölçekli işletmeler  
            "Small Business", # Küçük işletmeler
            "Individual",     # Bireysel müşteriler
            "High Value",     # Yüksek değer
            "Medium Value",   # Orta değer
            "Low Value",      # Düşük değer
            "Unassigned"
        ]
        
        # Tüm organizasyonlar için kategorileri oluştur
        for organisation in UserProfile.objects.all():
            self.stdout.write(f'Creating categories for {organisation.user.username}...')
            
            # Kaynak kategorilerini oluştur
            for category_name in source_categories:
                source_cat, created = SourceCategory.objects.get_or_create(
                    name=category_name,
                    organisation=organisation
                )
                if created:
                    self.stdout.write(f'  Created source category: {category_name}')
            
            # Değer kategorilerini oluştur
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
