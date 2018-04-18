from __future__ import absolute_import
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'opbeans.settings')

import django
django.setup()

app = Celery('opbeans')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()


from elasticsearch_dsl.connections import connections
from django.conf import settings

connections.create_connection(hosts=settings.ELASTICSEARCH_URL)
