import os
from django.urls import re_path, include
from django.contrib import admin
from django.conf import settings
from django.views.static import serve

from opbeans import views

urlpatterns = [
    re_path(r"^admin/", admin.site.urls),
    re_path(r"^$", views.home),
    re_path(r"^(?:dashboard|products|customers|orders).*$", views.home),
    re_path(r"^api/stats$", views.stats, name="stats"),
    re_path(r"^api/products$", views.products, name="products"),
    re_path(r"^api/products/top$", views.top_products, name="top-products"),
    re_path(r"^api/products/(?P<pk>[0-9]+)$", views.product, name="product-detail"),
    re_path(
        r"^api/products/(?P<pk>[0-9]+)/customers$",
        views.product_customers,
        name="product-customers",
    ),
    re_path(r"^api/types$", views.product_types, name="product-types"),
    re_path(
        r"^api/types/(?P<pk>[0-9]+)$", views.product_type, name="product-type-detail"
    ),
    re_path(r"^api/customers$", views.customers, name="customers"),
    re_path(r"^api/customers/(?P<pk>[0-9]+)$", views.customer, name="customer=detail"),
    re_path(r"^api/orders$", views.orders, name="orders"),
    re_path(r"^api/orders/csv$", views.post_order_csv, name="orders-csv"),
    re_path(r"^api/orders/(?P<pk>[0-9]+)$", views.order, name="order-detail"),
    re_path(
        r"^images/(?P<path>.*)$",
        serve,
        kwargs={
            "document_root": os.path.join(
                settings.BASE_DIR, "opbeans", "static", "build", "images"
            )
        },
    ),
    re_path(r"^oopsie$", views.oopsie),
    re_path(r"^labeldelay$", views.label_with_delay),
    re_path("", include("django_prometheus.urls")),
]
