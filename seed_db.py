import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql_crm.settings')
django.setup()

from crm.models import Customer, Product

# Seed Customers
Customer.objects.create(name="Test User", email="test@example.com", phone="+1234567890")

# Seed Products
Product.objects.create(name="Laptop", price=999.99, stock=5)
Product.objects.create(name="Mouse", price=19.99, stock=100)

print("Database seeded successfully!")
