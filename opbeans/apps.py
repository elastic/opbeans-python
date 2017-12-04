from django.conf import settings
from django.apps import AppConfig

from elasticsearch_dsl.connections import connections


class OpbeansAppConfig(AppConfig):
    name = 'opbeans'

    def ready(self):
        if settings.ELASTICSEARCH_URL:
            connections.create_connection(hosts=settings.ELASTICSEARCH_URL)
