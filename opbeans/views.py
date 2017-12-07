import json

from django.http import JsonResponse, Http404, HttpResponse
from django.core.cache import cache
from django.db import models
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from opbeans import models as m
from opbeans import utils


def stats(request):
    data = cache.get(utils.stats.cache_key)
    if not data:
        data = utils.stats()
        cache.set(utils.stats.cache_key, data, 60)
    return JsonResponse(data, safe=False)


def products(request):
    product_list = m.Product.objects.select_related('product_type')
    data = list(product_list.values('id', 'sku', 'name', 'stock', 'product_type__name'))
    for elem in data:
        elem['type_name'] = elem.pop('product_type__name')
    return JsonResponse(data, safe=False)


def top_products(request):
    products = m.Product.objects.annotate(
        sold=models.Sum('orderline__amount')
    ).order_by('-sold').values(
        'id', 'sku', 'name', 'stock', 'sold'
    )[:3]
    return JsonResponse(list(products), safe=False)


def product(request, pk):
    try:
        product_obj = m.Product.objects.select_related(
            'product_type'
        ).filter(
            pk=pk
        ).values(
            'id', 'sku', 'name', 'description', 'product_type_id',
            'product_type__name', 'stock', 'cost', 'selling_price',
        )[0]
    except IndexError:
        raise Http404()
    product_obj['type_id'] = product_obj.pop('product_type_id')
    product_obj['type_name'] = product_obj.pop('product_type__name')
    return JsonResponse(product_obj)


def product_customers(request, pk):
    try:
        limit = int(request.GET.get('count', 1000))
    except ValueError:
        limit = 1000
    customers_list = m.Customer.objects.filter(
        orders__orderline__product_id=pk
    ).distinct().values(
        'id', 'full_name', 'company_name', 'email', 'address',
        'postal_code', 'city', 'country'
    )[:limit]
    return JsonResponse(list(customers_list), safe=False)


def product_types(request):
    types = m.ProductType.objects.values('id', 'name')
    return JsonResponse(list(types), safe=False)


def product_type(request, pk):
    product_type = get_object_or_404(m.ProductType, pk=pk)
    products = m.Product.objects.filter(product_type=product_type).values(
        'id', 'name'
    )
    data = {
        'id': product_type.pk,
        'name': product_type.name,
        'products': list(products),
    }
    return JsonResponse(data)


def customers(request):
    customer_list = m.Customer.objects.values(
        'id', 'full_name', 'company_name', 'email', 'address',
        'postal_code', 'city', 'country'
    )
    return JsonResponse(list(customer_list), safe=False)


def customer(request, pk):
    try:
        customer_obj = m.Customer.objects.filter(pk=pk).values(
            'id', 'full_name', 'company_name', 'email', 'address',
            'postal_code', 'city', 'country'
        )[0]
    except IndexError:
        raise Http404()
    return JsonResponse(customer_obj)


@csrf_exempt
def orders(request):
    if request.method == 'POST':
        return post_order(request)
    order_list = list(m.Order.objects.values(
        'id', 'customer_id', 'customer__full_name', 'created_at'
    )[:1000])
    for order in order_list:
        order['customer_name'] = order.pop('customer__full_name')
    return JsonResponse(order_list, safe=False)


def post_order(request):
    data = json.loads(request.body)
    if 'customer_id' not in data:
        return HttpResponse(status=400)
    customer_obj = get_object_or_404(m.Customer, pk=data['customer_id'])
    order_obj = m.Order.objects.create(customer=customer_obj)
    for line in data['lines']:
        product_obj = get_object_or_404(m.Product, pk=line['id'])
        m.OrderLine.objects.create(
            order=order_obj,
            product=product_obj,
            amount=line['amount']
        )
    return JsonResponse({'id': order_obj.pk})


def order(request, pk):
    order_obj = get_object_or_404(m.Order, pk=pk)
    lines = list(order_obj.orderline_set.values(
        'product_id', 'amount', 'product__sku', 'product__name', 'product__description', 'product__product_type_id',
        'product__stock', 'product__cost', 'product__selling_price',
    ))
    for line in lines:
        line['id'] = line.pop('product_id')
        line['sku'] = line.pop('product__sku')
        line['name'] = line.pop('product__name')
        line['description'] = line.pop('product__description')
        line['type_id'] = line.pop('product__product_type_id')
        line['stock'] = line.pop('product__stock')
        line['cost'] = line.pop('product__cost')
        line['selling_price'] = line.pop('product__selling_price')
    data = {
        'id': order_obj.pk,
        'created_at': order_obj.created_at,
        'customer_id': order_obj.customer_id,
        'lines': lines,
    }
    return JsonResponse(data)


def oopsie(request):
    assert False