import graphene
from graphene_django import DjangoObjectType
from .models import Customer, Product, Order
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db import transaction
import re

# Object Types
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer

class ProductType(DjangoObjectType):
    class Meta:
        model = Product

class OrderType(DjangoObjectType):
    class Meta:
        model = Order

# Mutations

# 1. Create Customer
class CreateCustomer(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String()

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, name, email, phone=None):
        if Customer.objects.filter(email=email).exists():
            raise Exception("Email already exists.")

        if phone:
            if not re.match(r'^(\+?\d{10,15}|\d{3}-\d{3}-\d{4})$', phone):
                raise Exception("Invalid phone format.")

        customer = Customer.objects.create(name=name, email=email, phone=phone)
        return CreateCustomer(customer=customer, message="Customer created successfully.")

# 2. Bulk Create Customers
class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(graphene.JSONString, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        created_customers = []
        errors = []

        with transaction.atomic():
            for idx, data in enumerate(input):
                try:
                    name = data.get("name")
                    email = data.get("email")
                    phone = data.get("phone")

                    if not name or not email:
                        errors.append(f"Record {idx+1}: Name and Email are required.")
                        continue

                    validate_email(email)

                    if Customer.objects.filter(email=email).exists():
                        errors.append(f"Record {idx+1}: Email already exists.")
                        continue

                    if phone and not re.match(r'^(\+?\d{10,15}|\d{3}-\d{3}-\d{4})$', phone):
                        errors.append(f"Record {idx+1}: Invalid phone format.")
                        continue

                    customer = Customer.objects.create(name=name, email=email, phone=phone)
                    created_customers.append(customer)

                except Exception as e:
                    errors.append(f"Record {idx+1}: {str(e)}")

        return BulkCreateCustomers(customers=created_customers, errors=errors)

# 3. Create Product
class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Float(required=True)
        stock = graphene.Int()

    product = graphene.Field(ProductType)

    def mutate(self, info, name, price, stock=0):
        if price <= 0:
            raise Exception("Price must be positive.")
        if stock < 0:
            raise Exception("Stock cannot be negative.")

        product = Product.objects.create(name=name, price=price, stock=stock)
        return CreateProduct(product=product)

# 4. Create Order
class CreateOrder(graphene.Mutation):
    class Arguments:
        customer_id = graphene.ID(required=True)
        product_ids = graphene.List(graphene.ID, required=True)
        order_date = graphene.DateTime()

    order = graphene.Field(OrderType)

    def mutate(self, info, customer_id, product_ids, order_date=None):
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            raise Exception("Invalid customer ID.")

        products = Product.objects.filter(id__in=product_ids)
        if not products.exists():
            raise Exception("Invalid product IDs.")

        total_amount = sum([p.price for p in products])

        order = Order.objects.create(customer=customer, total_amount=total_amount)
        order.products.set(products)

        return CreateOrder(order=order)

# Query and Mutation Setup
class Query(graphene.ObjectType):
    hello = graphene.String()
    customers = graphene.List(CustomerType)
    products = graphene.List(ProductType)
    orders = graphene.List(OrderType)

    def resolve_hello(root, info):
        return "Hello, GraphQL!"

    def resolve_customers(root, info):
        return Customer.objects.all()

    def resolve_products(root, info):
        return Product.objects.all()

    def resolve_orders(root, info):
        return Order.objects.all()

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
