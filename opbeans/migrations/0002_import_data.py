import subprocess
import os
import json

from django.conf import settings
from django.db import migrations


def load_fixture(apps, schema_editor):

    _get_model = apps.get_model

    models = {
        _get_model("opbeans.customer"): [],
        _get_model("opbeans.producttype"): [],
        _get_model("opbeans.product"): [],
        _get_model("opbeans.order"): [],
        _get_model("opbeans.orderline"): [],
    }

    renames = {
        "order": "order_id",
        "customer": "customer_id",
        "product_type": "product_type_id",
        "product": "product_id",
    }

    file = os.path.join(settings.BASE_DIR, "opbeans/migrations/initial_data.json")
    try:
        subprocess.check_call(["bunzip2", "-k", file + ".bz2"])
        with open(file) as f:
            data = json.load(f)
        for item in data:
            model = _get_model(item["model"])
            for orig, rename in renames.items():
                if orig in item["fields"]:
                    item["fields"][rename] = item["fields"].pop(orig)
            models[model].append(model(id=item["pk"], **item["fields"]))
        for model, bulk_list in models.items():
            model.objects.bulk_create(bulk_list)
    finally:
        if os.path.exists(file):
            os.unlink(file)
    tables = tuple(m._meta.db_table for m in models.keys())

    # recalculate sequences in postgres
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute("""
            SELECT 'SELECT SETVAL(' ||
                   quote_literal(quote_ident(PGT.schemaname) || '.' || quote_ident(S.relname)) ||
                   ', COALESCE(MAX(' ||quote_ident(C.attname)|| '), 1) ) FROM ' ||
                   quote_ident(PGT.schemaname)|| '.'||quote_ident(T.relname)|| ';'
            FROM pg_class AS S,
                 pg_depend AS D,
                 pg_class AS T,
                 pg_attribute AS C,
                 pg_tables AS PGT
            WHERE S.relkind = 'S'
                AND S.oid = D.objid
                AND D.refobjid = T.oid
                AND D.refobjid = C.attrelid
                AND D.refobjsubid = C.attnum
                AND T.relname = PGT.tablename
                AND T.relname in %s
            ORDER BY S.relname;""",
        params=(tables,))



class Migration(migrations.Migration):
    dependencies = [
        ("opbeans", "0001_initial")
    ]

    operations = [
        migrations.RunPython(load_fixture),
    ]
