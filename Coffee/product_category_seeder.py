# DISREGARD THIS FILE SINCE THIS IS A SEEDER FOR PRODUCTS AND CATEGORIES RUN INTO THE SHELL, NOT A VIEW
from products.models import Category, Product
import random

product_data = {
    'Bakery': ['Scone', 'Biscotti', 'Pastry'],
    'Branded': ['Housewares', 'Clothing'],
    'Coffee': ['Gourmet brewed coffee', 'Drip coffee', 'Barista Espresso', 'Organic brewed coffee', 'Premium brewed coffee'],
    'Coffee beans': ['Gourmet Beans', 'Organic Beans', 'Premium Beans', 'Green beans', 'Espresso Beans', 'House blend Beans'],
    'Drinking Chocolate': ['Hot chocolate'],
    'Flavours': ['Regular syrup', 'Sugar free syrup'],
    'Loose Tea': ['Herbal tea', 'Chai tea', 'Green tea', 'Black tea'],
    'Packaged Chocolate': ['Drinking Chocolate', 'Organic Chocolate'],
    'Tea': ['Brewed Chai tea', 'Brewed Black tea', 'Brewed Green tea', 'Brewed herbal tea']
}

total_seeded = 0
for cat_name, products in product_data.items():
    category, _ = Category.objects.get_or_create(category_name=cat_name)
    print(f"[+] Category: {category.category_name}")
    
    for prod_name in products:
        product, created = Product.objects.get_or_create(
            category=category,
            product_name=prod_name,
            defaults={'available': random.randint(20, 150)}
        )
        if created:
            total_seeded += 1
            print(f"    -> Product: {product.product_name}")

print(f"\nSUCCESS: Added {total_seeded} products!")
