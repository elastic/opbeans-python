import json
import os

from django.apps import apps
from django.conf import settings

RUM_CONFIG = None


def rum_settings(request):
    global RUM_CONFIG
    if RUM_CONFIG:
        return RUM_CONFIG
    url = os.environ.get('ELASTIC_APM_JS_BASE_SERVER_URL', os.environ.get('ELASTIC_APM_JS_SERVER_URL'))
    if not url:
        app = apps.get_app_config('elasticapm.contrib.django')
        url = app.client.config.server_url
    with open(os.path.join(settings.BASE_DIR, 'opbeans', 'static', 'package.json')) as f:
        package_json = json.load(f)
    service_name = os.environ.get('ELASTIC_APM_JS_BASE_SERVICE_NAME', package_json['name'])
    service_version = os.environ.get('ELASTIC_APM_JS_BASE_SERVICE_VERSION', package_json['version'])
    RUM_CONFIG = {
        "RUM_SERVICE_NAME": service_name,
        "RUM_SERVICE_VERSION": service_version,
        "RUM_SERVER_URL": url
    }
    return RUM_CONFIG
