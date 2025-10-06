import re
import graphene
from graphene_django import DjangoObjectType
from .models import Customer, Product, Order
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from graphene_django.filter import DjangoFilterConnectionField
from .filters import CustomerFilter, ProductFilter, OrderFilter
from crm.models import Product


# TYPES
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer

class ProductType(DjangoObjectType):
    class Meta:
        model = Product

class OrderType(DjangoObjectType):
    class Meta:
        model = Order

# INPUTS
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Decimal(required=True)
    stock = graphene.Int()

class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.String()

# MUTATIONS
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, input):
        if Customer.objects.filter(email=input.email).exists():
            raise Exception("Email already exists")
        if input.phone and not re.match(r"^\+?\d[\d\-]{7,}$", input.phone):
            raise Exception("Invalid phone format")

        customer = Customer(
            name=input.name,
            email=input.email,
            phone=input.phone
        )
        customer.save()   # ✅ Explicit save()
        return CreateCustomer(customer=customer, message="Customer created successfully!")

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        created_customers = []
        errors = []
        with transaction.atomic():
            for data in input:
                try:
                    if Customer.objects.filter(email=data.email).exists():
                        errors.append(f"Duplicate email: {data.email}")
                        continue
                    customer = Customer(
                        name=data.name,
                        email=data.email,
                        phone=data.phone
                    )
                    customer.save()   # ✅ Explicit save()
                    created_customers.append(customer)
                except Exception as e:
                    errors.append(str(e))
        return BulkCreateCustomers(customers=created_customers, errors=errors)

class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)

    def mutate(self, info, input):
        if input.price <= 0:
            raise Exception("Price must be positive")
        if input.stock is not None and input.stock < 0:
            raise Exception("Stock cannot be negative")

        product = Product(
            name=input.name,
            price=input.price,
            stock=input.stock if input.stock is not None else 0
        )
        product.save()   # ✅ Explicit save()
        return CreateProduct(product=product)

class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    order = graphene.Field(OrderType)

    def mutate(self, info, input):
        try:
            customer = Customer.objects.get(id=input.customer_id)
        except Customer.DoesNotExist:
            raise Exception("Customer not found")

        products = Product.objects.filter(id__in=input.product_ids)
        if not products:
            raise Exception("No valid products found")

        total = sum([p.price for p in products])

        order = Order(
            customer=customer,
            total_amount=total,
            order_date=input.order_date or timezone.now()
        )
        order.save()   # ✅ Explicit save()
        order.products.set(products)
        return CreateOrder(order=order)

# QUERY
class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hello, GraphQL!")
    all_customers = graphene.List(CustomerType)
    all_products = graphene.List(ProductType)
    all_orders = graphene.List(OrderType)

    def resolve_all_customers(self, info):
        return Customer.objects.all()

    def resolve_all_products(self, info):
        return Product.objects.all()

    def resolve_all_orders(self, info):
        return Order.objects.all()

# MAIN MUTATION
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
    update_low_stock_products = UpdateLowStockProducts.Field()

class UpdateLowStockProducts(graphene.Mutation):
    success = graphene.String()
    updated_products = graphene.List(graphene.String)

    def mutate(self, info):
        low_stock = Product.objects.filter(stock__lt=10)
        updated = []
        for product in low_stock:
            product.stock += 10
            product.save()
            updated.append(f"{product.name}: {product.stock}")
        return UpdateLowStockProducts(success="Stock updated", updated_products=updated)

