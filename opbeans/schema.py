# cookbook/ingredients/schema.py
import graphene

from graphene_django.types import DjangoObjectType

from opbeans import models


class CustomerType(DjangoObjectType):
    class Meta:
        model = models.Customer


class ProductType(DjangoObjectType):
    class Meta:
        model = models.Product


class ProductTypeType(DjangoObjectType):
    class Meta:
        model = models.ProductType


class OrderType(DjangoObjectType):
    class Meta:
        model = models.Order


class OrderLineType(DjangoObjectType):
    class Meta:
        model = models.OrderLine


class Query(graphene.ObjectType):
    all_customers = graphene.List(CustomerType)
    all_products = graphene.List(ProductType)
    all_product_types = graphene.List(ProductTypeType)

    def resolve_all_customers(self, info, **kwargs):
        return models.Customer.objects.all()

    def resolve_all_products(self, info, **kwargs):
        return models.Product.objects.select_related('product_type').all()

    def resolve_all_product_types(self, info, **kwargs):
        return models.ProductType.objects.all()


schema = graphene.Schema(query=Query)
