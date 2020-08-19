import os
from django.conf.urls import url
from django.contrib import admin
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.static import serve

from graphene_django.views import GraphQLView
from opbeans import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.home),
    url(r'^(?:dashboard|products|customers|orders).*$', views.home),
    url(r'^api/stats$', views.stats, name='stats'),
    url(r'^api/products$', views.products, name='products'),
    url(r'^api/products/top$', views.top_products, name='top-products'),
    url(r'^api/products/(?P<pk>[0-9]+)$', views.product, name='product-detail'),
    url(r'^api/products/(?P<pk>[0-9]+)/customers$', views.product_customers, name='product-customers'),
    url(r'^api/types$', views.product_types, name='product-types'),
    url(r'^api/types/(?P<pk>[0-9]+)$', views.product_type, name='product-type-detail'),
    url(r'^api/customers$', views.customers, name='customers'),
    url(r'^api/customers/(?P<pk>[0-9]+)$', views.customer, name='customer=detail'),
    url(r'^api/orders$', views.orders, name='orders'),
    url(r'^api/orders/csv$', views.post_order_csv, name='orders-csv'),
    url(r'^api/orders/(?P<pk>[0-9]+)$', views.order, name='order-detail'),
    url(r'^images/(?P<path>.*)$', serve, kwargs={'document_root': os.path.join(settings.BASE_DIR, 'opbeans', 'static', 'build', 'images')}),
    url(r'^oopsie$', views.oopsie),
    url(r'^graphql$', csrf_exempt(GraphQLView.as_view(graphiql=True))),
]
