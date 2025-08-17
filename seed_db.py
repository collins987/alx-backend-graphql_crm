import os
import django
import random
from decimal import Decimal
from datetime import datetime, timedelta

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alx_backend_graphql_crm.settings")
django.setup()

from crm.models import Customer, Product, Order


def seed_customers():
    customers_data = [
        {"name": "Alice Johnson", "email": "alice@example.com", "phone": "+1234567890"},
        {"name": "Bob Smith", "email": "bob@example.com", "phone": "123-456-7890"},
        {"name": "Carol Lee", "email": "carol@example.com", "phone": "+1987654321"},
        {"name": "David Kim", "email": "david@example.com"},
        {"name": "Eva Brown", "email": "eva@example.com"},
    ]
    customers = []
    for data in customers_data:
        obj, created = Customer.objects.get_or_create(email=data["email"], defaults=data)
        customers.append(obj)
    print(f"✅ Seeded {len(customers)} customers")
    return customers


def seed_products():
    products_data = [
        {"name": "Laptop", "price": Decimal("999.99"), "stock": 10},
        {"name": "Phone", "price": Decimal("499.99"), "stock": 25},
        {"name": "Headphones", "price": Decimal("79.99"), "stock": 50},
        {"name": "Monitor", "price": Decimal("199.99"), "stock": 15},
        {"name": "Keyboard", "price": Decimal("49.99"), "stock": 100},
    ]
    products = []
    for data in products_data:
        obj, created = Product.objects.get_or_create(name=data["name"], defaults=data)
        products.append(obj)
    print(f"✅ Seeded {len(products)} products")
    return products


def seed_orders(customers, products):
    orders = []
    for customer in customers:
        # pick 1–3 random products for each order
        chosen_products = random.sample(products, random.randint(1, 3))
        total_amount = sum([p.price for p in chosen_products])
        order_date = datetime.now() - timedelta(days=random.randint(1, 30))

        order = Order.objects.create(
            customer=customer,
            total_amount=total_amount,
            order_date=order_date
        )
        order.products.set(chosen_products)
        orders.append(order)
    print(f"✅ Seeded {len(orders)} orders")
    return orders


if __name__ == "__main__":
    print("🚀 Starting database seeding...")
    customers = seed_customers()
    products = seed_products()
    seed_orders(customers, products)
    print("🎉 Database seeding complete!")
