import random

from django.core.cache import cache

from celery.decorators import task

from opbeans import utils


@task()
def update_stats():
    if random.random() > 0.8:
        assert False, "Bad luck!"
    cache.set(utils.stats.cache_key, utils.stats(), 60)