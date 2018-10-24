import random

from django.core.cache import cache
from django.db import models as m

from celery.decorators import task
from elasticsearch import TransportError
from elasticsearch.helpers import bulk
from elasticsearch_dsl import Search
from elasticsearch_dsl.connections import connections

from opbeans import utils, models, documents


@task()
def update_stats():
    if random.random() > 0.8:
        assert False, "Bad luck!"
    cache.set(utils.stats.cache_key, utils.stats(), 60)


@task()
def sync_customers():
    customer_docs = []
    for customer in models.Customer.objects.annotate(total_orders=m.Count('orders')).order_by('pk')[50:]:
        customer_docs.append(documents.Customer(**customer.to_search()).to_dict(include_meta=True))
    bulk(connections.get_connection(), customer_docs)


@task()
def sync_orders():
    highest_id = None
    try:
        r = Search(index='py-orders').sort('-_id')[0].execute()
        highest_id = int(r.hits[0].meta.id)
    except TransportError as e:
        if e.status_code == 404:
            highest_id = 0
    order_docs = []
    for order in models.Order.objects.filter(id__gt=highest_id).prefetch_related('customer'):
        order_docs.append(documents.Order(**order.to_search()).to_dict(include_meta=True))
    bulk(connections.get_connection(), order_docs)
