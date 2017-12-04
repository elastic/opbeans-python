import random

from django.core.cache import cache
from django.db import models as m

from celery.decorators import task
from elasticsearch.helpers import bulk
from elasticsearch_dsl.connections import connections

from opbeans import utils, models, documents


@task()
def update_stats():
    if random.random() > 0.8:
        assert False, "Bad luck!"
    cache.set(utils.stats.cache_key, utils.stats(), 60)


@task()
def sync_customers():
    for customer in models.Customer.objects.all().order_by('pk')[:50]:
        customer_doc = documents.Customer(**customer.to_search())
        customer_doc['total_orders'] = models.Order.objects.filter(customer=customer_doc._id).count()
        customer_doc.save()


@task()
def sync_customers_bulk():
    customer_docs = []
    for customer in models.Customer.objects.annotate(total_orders=m.Count('orders')).order_by('pk')[50:]:
        customer_docs.append(documents.Customer(**customer.to_search()).to_dict(include_meta=True))
    bulk(connections.get_connection(), customer_docs)
