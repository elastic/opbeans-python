from django.db import models

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