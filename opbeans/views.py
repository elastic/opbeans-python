import os
import json
import time
from functools import wraps
import random

import prometheus_client
from django.http import JsonResponse, Http404, HttpResponse
from django.conf import settings
from django.core.cache import cache
from django.db import models
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt

import elasticapm
from elasticapm.contrib.django.client import client
try:
    from elasticapm import label
except ImportError:
    # elastic-apm < 5.0
    from elasticapm import tag as label
import requests
import structlog

from opbeans import models as m
from opbeans import utils
from opbeans.utils import StreamingJsonResponse, iterlist

logger = structlog.get_logger(__name__)


def maybe_dt(view_func):
    """
    Either calls the view, or randomly forwards the request to another opbeans service
    """
    other_services = [s for s in os.environ.get("OPBEANS_SERVICES", "").split(",") if s and "opbeans-python" not in s]
    if other_services:
        logger.info("Registered Opbeans Services: {}".format(", ".join(other_services)))
    else:
        logger.info("dt_ping_pong_disabled", reason="no_services_discovered")
    try:
        probability = float(os.environ.get("OPBEANS_DT_PROBABILITY", 0.5))
    except ValueError:
        probability = 0.5

    def wrapped_view(request, *args, **kwargs):
        r = random.random()
        logger.info("dt_ping_pong_dice_throw", random_val=r, probability=probability, passed=bool(r < probability))
        if request.method == "GET" and other_services and r < probability:
            other_service = random.choice(other_services)
            if not other_service.startswith("http://"):
                other_service = "http://{}:3000".format(other_service)
            url = other_service + request.get_full_path()
            logger.info("dt_ping_pong_proxy", url=url)
            try:
                other_response = requests.get(url, timeout=15)
            except requests.exceptions.Timeout:
                logger.error("dt_ping_pong_timeout", service=other_service)
                raise
            except Exception:
                logger.error("dt_ping_pong_connection_failed", service=other_service)
                raise
            try:
                content_type = other_response.headers['content-type']
            except KeyError:
                logger.debug("dt_ping_pong_missing_content_type", service=other_service)
                content_type = "text/plain"
            return HttpResponse(other_response.content, status=other_response.status_code, content_type=content_type)
        return view_func(request, *args, **kwargs)
    return wraps(view_func)(wrapped_view)


@maybe_dt
def stats(request):
    from_cache = True
    data = cache.get(utils.stats.cache_key)
    if not data:
        data = utils.stats()
        cache.set(utils.stats.cache_key, data, 60)
        from_cache = False
    label(served_from_cache=from_cache)
    return JsonResponse(data, safe=False)


random_summary = prometheus_client.Summary("random_summary", "Random summary", ["a"])
random_counter = prometheus_client.Counter("random_counter", "Random counter", ["a"])
random_gauge = prometheus_client.Gauge("random_gauge", "Random gauge", ["a"])

@maybe_dt
def products(request):
    product_list = m.Product.objects.all()

    random_summary.labels(a=random.choice("xyz")).observe(random.randint(0, 100))
    random_counter.labels(a=random.choice("xyz")).inc(random.randint(0, 5))
    random_gauge.labels(a=random.choice("xzy")).set(random.random()*100)
    data = iterlist({
        'id': elem.id,
        'sku': elem.sku,
        'name': elem.name,
        'stock': elem.stock,
        'type_name': elem.product_type.name,
    } for elem in product_list)

    return StreamingJsonResponse(data, safe=False)


@maybe_dt
def top_products(request):
    products = m.Product.objects.annotate(
        sold=models.Sum('orderline__amount')
    ).order_by('-sold').values(
        'id', 'sku', 'name', 'stock', 'sold'
    )[:3]
    return JsonResponse(list(products), safe=False)


@maybe_dt
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


@maybe_dt
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


@maybe_dt
def product_types(request):
    types = m.ProductType.objects.values('id', 'name')
    return JsonResponse(list(types), safe=False)


@maybe_dt
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


@maybe_dt
def customers(request):
    customer_list = m.Customer.objects.values(
        'id', 'full_name', 'company_name', 'email', 'address',
        'postal_code', 'city', 'country'
    )
    return JsonResponse(list(customer_list), safe=False)


@maybe_dt
def customer(request, pk):
    try:
        customer_obj = m.Customer.objects.filter(pk=pk).values(
            'id', 'full_name', 'company_name', 'email', 'address',
            'postal_code', 'city', 'country'
        )[0]
    except IndexError:
        logger.warning('customer_not_found', customer_id=pk, exc_info=True)
        raise Http404()
    return JsonResponse(customer_obj)


@csrf_exempt
def orders(request):
    if request.method == 'POST':
        # set transaction name to post_order
        elasticapm.set_transaction_name('POST opbeans.views.post_order')
        return post_order(request)
    order_list = list(m.Order.objects.values(
        'id', 'customer_id', 'customer__full_name', 'created_at'
    )[:1000])
    for order_dict in order_list:
        order_dict['customer_name'] = order_dict.pop('customer__full_name')
    return JsonResponse(order_list, safe=False)

line_item_counter = prometheus_client.Counter("opbeans_python_line_items", "Counter of line items")
order_summary = prometheus_client.Summary("opbeans_python_orders", "Summary of orders and total order values")


def post_order(request):
    data = json.loads(request.body)
    if 'customer_id' not in data:
        return HttpResponse(status=400)
    customer_obj = get_object_or_404(m.Customer, pk=data['customer_id'])
    order_obj = m.Order.objects.create(customer=customer_obj)

    total_amount = 0
    for line in data['lines']:
        product_obj = get_object_or_404(m.Product, pk=line['id'])
        m.OrderLine.objects.create(
            order=order_obj,
            product=product_obj,
            amount=line['amount']
        )
        total_amount += line['amount'] * product_obj.selling_price

    # store lines count in and total amount in tags
    label(
        lines_count=len(data['lines']),
        total_amount=total_amount / 100.0,
    )
    line_item_counter.inc(len(data['lines']))
    order_summary.observe(total_amount / 100.0)

    # store customer in transaction custom data
    elasticapm.set_custom_context({
        'customer_name': customer_obj.full_name,
        'customer_email': customer_obj.email,
    })
    return JsonResponse({'id': order_obj.pk})


@csrf_exempt
def post_order_csv(request):
    customer_id = request.POST['customer']
    customer_obj = get_object_or_404(m.Customer, pk=customer_id)
    order_obj = m.Order.objects.create(customer=customer_obj)
    total_amount = 0
    i = 0
    for i, line in enumerate(request.FILES['file']):
        product_id, amount = map(int, line.decode('utf8').split(','))
        product_obj = get_object_or_404(m.Product, pk=product_id)
        m.OrderLine.objects.create(
            order=order_obj,
            product=product_obj,
            amount=amount
        )
        total_amount += amount * product_obj.selling_price
    label(
        lines_count=i,
        total_amount=total_amount / 100.0,
    )
    return HttpResponse('OK')


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
    client.capture_message('About to blow up!')
    try:
        1 / 0
    except ZeroDivisionError:
        try:
            1 + "a"
        except TypeError:
            raise AssertionError("oh no")



def home(request):
    with elasticapm.capture_span("hard-home-work"):
        time.sleep(random.random() / 2.0)
    return render(request, "index.html")


def label_with_delay(request):
    labels = {}
    for k, v in request.GET.items():
        if k != "delay":
            labels[k] = v
    with elasticapm.capture_span("delayed-and-labeled", labels=labels):
        if "delay" in request.GET:
            time.sleep(float(request.GET["delay"]) / 1000.0)
    return HttpResponse("OK")

