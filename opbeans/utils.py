from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.http import StreamingHttpResponse

from opbeans import models as m


def stats():
    numbers = m.Product.objects.annotate(
        order_count=models.Count('order'),
        per_item_profit=models.F('selling_price') - models.F('cost')
    ).annotate(
        total_profit=models.F('order_count') * models.F('per_item_profit'),
        total_revenue=models.F('order_count') * models.F('selling_price'),
        total_cost=models.F('order_count') * models.F('cost')
    ).aggregate(
        revenue=models.Sum('total_revenue'),
        cost=models.Sum('total_cost'),
        profit=models.Sum('total_profit'),
    )
    data = {
        'products': m.Product.objects.count(),
        'customers': m.Customer.objects.count(),
        'orders': m.Order.objects.count(),
        'numbers': numbers
    }
    return data


stats.cache_key = 'shop-stats'


class iterlist(list):
    def __init__(self, iterator):
        self.iterator = iterator
        super(iterlist, self).__init__("Hack")

    def __iter__(self):
        return self.iterator


class StreamingJsonResponse(StreamingHttpResponse):
    def __init__(self, data, encoder=DjangoJSONEncoder, safe=True,
                 json_dumps_params=None, *args, **kwargs):
        if safe and not isinstance(data, dict):
            raise TypeError(
                'In order to allow non-dict objects to be serialized set the '
                'safe parameter to False.'
            )
        kwargs.setdefault('content_type', 'application/json')
        encoder_obj = encoder(**(json_dumps_params or {}))
        iterator = encoder_obj.iterencode(data)
        super(StreamingJsonResponse, self).__init__(iterator, *args, **kwargs)