import json

from django.conf import settings
from django import template

register = template.Library()

with open(settings.ASSET_MANIFEST) as manifest_file:
    manifest = json.load(manifest_file)


@register.simple_tag
def asset(path):
    if path in manifest:
        return '/' + manifest[path]
    return ''
