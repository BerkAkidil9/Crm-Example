from django.core.management.base import BaseCommand
from ProductsAndStock.models import Category, SubCategory

class Command(BaseCommand):
    help = 'Create sample categories and subcategories'

    def handle(self, *args, **options):
        # Define categories with their subcategories
        categories_data = [
            {
                'name': 'Electronics',
                'description': 'Electronic devices and gadgets',
                'icon': 'fas fa-laptop',
                'subcategories': [
                    {'name': 'Smartphones', 'description': 'Mobile phones and accessories'},
                    {'name': 'Laptops', 'description': 'Portable computers and accessories'},
                    {'name': 'Tablets', 'description': 'Tablet computers and accessories'},
                    {'name': 'Audio', 'description': 'Headphones, speakers, and audio equipment'},
                    {'name': 'Cameras', 'description': 'Digital cameras and photography equipment'},
                    {'name': 'Gaming', 'description': 'Gaming consoles and accessories'},
                ]
            },
            {
                'name': 'Clothing',
                'description': 'Fashion and apparel',
                'icon': 'fas fa-tshirt',
                'subcategories': [
                    {'name': 'Men\'s Clothing', 'description': 'Clothing for men'},
                    {'name': 'Women\'s Clothing', 'description': 'Clothing for women'},
                    {'name': 'Children\'s Clothing', 'description': 'Clothing for children'},
                    {'name': 'Shoes', 'description': 'Footwear for all ages'},
                    {'name': 'Accessories', 'description': 'Bags, belts, jewelry, and other accessories'},
                    {'name': 'Sportswear', 'description': 'Athletic and sports clothing'},
                ]
            },
            {
                'name': 'Food & Beverages',
                'description': 'Food and drink products',
                'icon': 'fas fa-utensils',
                'subcategories': [
                    {'name': 'Fresh Produce', 'description': 'Fruits and vegetables'},
                    {'name': 'Meat & Seafood', 'description': 'Fresh and frozen meat and seafood'},
                    {'name': 'Dairy Products', 'description': 'Milk, cheese, yogurt, and dairy items'},
                    {'name': 'Bakery', 'description': 'Bread, pastries, and baked goods'},
                    {'name': 'Beverages', 'description': 'Drinks, juices, and liquid refreshments'},
                    {'name': 'Snacks', 'description': 'Chips, nuts, and snack foods'},
                ]
            },
            {
                'name': 'Home & Garden',
                'description': 'Home improvement and garden supplies',
                'icon': 'fas fa-home',
                'subcategories': [
                    {'name': 'Furniture', 'description': 'Tables, chairs, and home furniture'},
                    {'name': 'Decor', 'description': 'Home decoration and accessories'},
                    {'name': 'Kitchen & Dining', 'description': 'Kitchen utensils and dining accessories'},
                    {'name': 'Garden Tools', 'description': 'Tools for gardening and outdoor work'},
                    {'name': 'Plants', 'description': 'Indoor and outdoor plants'},
                    {'name': 'Cleaning Supplies', 'description': 'Household cleaning products'},
                ]
            },
            {
                'name': 'Sports & Outdoors',
                'description': 'Sports equipment and outdoor gear',
                'icon': 'fas fa-dumbbell',
                'subcategories': [
                    {'name': 'Fitness Equipment', 'description': 'Exercise machines and fitness gear'},
                    {'name': 'Team Sports', 'description': 'Balls, equipment for team sports'},
                    {'name': 'Outdoor Gear', 'description': 'Camping, hiking, and outdoor equipment'},
                    {'name': 'Water Sports', 'description': 'Swimming and water activity equipment'},
                    {'name': 'Winter Sports', 'description': 'Skiing, snowboarding, and winter gear'},
                    {'name': 'Cycling', 'description': 'Bicycles and cycling accessories'},
                ]
            },
            {
                'name': 'Books & Media',
                'description': 'Books, movies, music, and educational materials',
                'icon': 'fas fa-book',
                'subcategories': [
                    {'name': 'Books', 'description': 'Fiction and non-fiction books'},
                    {'name': 'Movies & TV', 'description': 'DVDs, Blu-rays, and streaming media'},
                    {'name': 'Music', 'description': 'CDs, vinyl records, and digital music'},
                    {'name': 'Educational', 'description': 'Textbooks and educational materials'},
                    {'name': 'Magazines', 'description': 'Periodicals and magazines'},
                    {'name': 'Games', 'description': 'Board games, puzzles, and entertainment'},
                ]
            },
            {
                'name': 'Health & Beauty',
                'description': 'Health, beauty, and personal care products',
                'icon': 'fas fa-heart',
                'subcategories': [
                    {'name': 'Skincare', 'description': 'Facial and body care products'},
                    {'name': 'Makeup', 'description': 'Cosmetics and beauty products'},
                    {'name': 'Hair Care', 'description': 'Shampoos, conditioners, and hair products'},
                    {'name': 'Personal Care', 'description': 'Hygiene and personal care items'},
                    {'name': 'Supplements', 'description': 'Vitamins and health supplements'},
                    {'name': 'Medical', 'description': 'First aid and medical supplies'},
                ]
            },
            {
                'name': 'Automotive',
                'description': 'Car parts, accessories, and automotive supplies',
                'icon': 'fas fa-car',
                'subcategories': [
                    {'name': 'Car Parts', 'description': 'Engine, brake, and other car components'},
                    {'name': 'Accessories', 'description': 'Car accessories and customization'},
                    {'name': 'Tools', 'description': 'Automotive tools and equipment'},
                    {'name': 'Maintenance', 'description': 'Oil, filters, and maintenance supplies'},
                    {'name': 'Electronics', 'description': 'Car audio, GPS, and electronic accessories'},
                    {'name': 'Tires', 'description': 'Tires and wheel accessories'},
                ]
            }
        ]

        created_categories = 0
        created_subcategories = 0

        for category_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=category_data['name'],
                defaults={
                    'description': category_data['description'],
                    'icon': category_data['icon']
                }
            )
            
            if created:
                created_categories += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created category: {category.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Category already exists: {category.name}')
                )

            # Create subcategories
            for subcat_data in category_data['subcategories']:
                subcategory, created = SubCategory.objects.get_or_create(
                    name=subcat_data['name'],
                    category=category,
                    defaults={'description': subcat_data['description']}
                )
                
                if created:
                    created_subcategories += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'  Created subcategory: {subcategory.name}')
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully created {created_categories} categories and {created_subcategories} subcategories!'
            )
        )
