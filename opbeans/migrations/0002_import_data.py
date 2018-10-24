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
    os.unlink(file)



class Migration(migrations.Migration):
    dependencies = [
        ("opbeans", "0001_initial")
    ]

    operations = [
        migrations.RunPython(load_fixture),
    ]
