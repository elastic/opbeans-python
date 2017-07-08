from __future__ import unicode_literals

from django.db import models


class Customer(models.Model):
    full_name = models.CharField(max_length=1000)
    company_name = models.CharField(max_length=1000)
    email = models.CharField(max_length=1000)
    address = models.CharField(max_length=1000)
    postal_code = models.CharField(max_length=1000)
    city = models.CharField(max_length=1000)
    country = models.CharField(max_length=1000)

    def __str__(self):
        return self.full_name

    class Meta:
        managed = False
        db_table = 'customers'


class OrderLine(models.Model):
    # watch out, hack: Django *really* wants a primary key, so we
    # pretend that "order_id" is it. This should be ok as long
    # as we only use this for read access
    order = models.ForeignKey('Order', models.DO_NOTHING, primary_key=True)
    product = models.ForeignKey('Product', models.DO_NOTHING)
    amount = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'order_lines'


class Order(models.Model):
    customer = models.ForeignKey(Customer, models.DO_NOTHING)
    created_at = models.DateTimeField()
    lines = models.ManyToManyField('Product', through=OrderLine)

    class Meta:
        managed = False
        db_table = 'orders'


class ProductType(models.Model):
    name = models.CharField(unique=True, max_length=1000)

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'product_types'


class Product(models.Model):
    sku = models.CharField(unique=True, max_length=1000)
    name = models.CharField(max_length=1000)
    description = models.TextField()
    product_type = models.ForeignKey(ProductType, models.DO_NOTHING, db_column='type_id')
    stock = models.IntegerField()
    cost = models.IntegerField()
    selling_price = models.IntegerField()

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'products'
