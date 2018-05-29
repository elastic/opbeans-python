import os

from django.apps import apps


def apm_settings(request):
    if 'ELASTIC_APM_JS_SERVER_URL' in os.environ:
        url = os.environ['ELASTIC_APM_JS_SERVER_URL']
    else:
        app = apps.get_app_config('elasticapm.contrib.django')
        url = app.client.config.server_url

    return {
        'ELASTIC_APM_SERVER_URL': url,
    }
