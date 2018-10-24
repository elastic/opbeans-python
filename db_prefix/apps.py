from django.conf import settings
from django.db.models.signals import class_prepared, pre_init
from django.apps import AppConfig

import logging

logger = logging.getLogger("opbeans")

def add_db_prefix(sender, **kwargs):
    prefix = getattr(settings, "DB_PREFIX", None)
    if prefix and not prefix.endswith("_"):
        prefix += "_"
    if prefix and not sender._meta.db_table.startswith(prefix):
        sender._meta.db_table = prefix + sender._meta.db_table


class DbPrefixApp(AppConfig):
    name = "db_prefix"

    def ready(self):
        pre_init.connect(add_db_prefix)
        class_prepared.connect(add_db_prefix)
        logger.info("CONNECTED PREFIX SIGNALS")

