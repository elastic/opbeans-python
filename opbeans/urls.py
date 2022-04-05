import os
from django.urls import path, include
from django.contrib import admin
from django.conf import settings
from django.views.static import serve

from opbeans import views

urlpatterns = [
    path(r"^admin/", admin.site.urls),
    path(r"^$", views.home),
    path(r"^(?:dashboard|products|customers|orders).*$", views.home),
    path(r"^api/stats$", views.stats, name="stats"),
    path(r"^api/products$", views.products, name="products"),
    path(r"^api/products/top$", views.top_products, name="top-products"),
    path(r"^api/products/(?P<pk>[0-9]+)$", views.product, name="product-detail"),
    path(
        r"^api/products/(?P<pk>[0-9]+)/customers$",
        views.product_customers,
        name="product-customers",
    ),
    path(r"^api/types$", views.product_types, name="product-types"),
    path(r"^api/types/(?P<pk>[0-9]+)$", views.product_type, name="product-type-detail"),
    path(r"^api/customers$", views.customers, name="customers"),
    path(r"^api/customers/(?P<pk>[0-9]+)$", views.customer, name="customer=detail"),
    path(r"^api/orders$", views.orders, name="orders"),
    path(r"^api/orders/csv$", views.post_order_csv, name="orders-csv"),
    path(r"^api/orders/(?P<pk>[0-9]+)$", views.order, name="order-detail"),
    path(
        r"^images/(?P<path>.*)$",
        serve,
        kwargs={
            "document_root": os.path.join(
                settings.BASE_DIR, "opbeans", "static", "build", "images"
            )
        },
    ),
    path(r"^oopsie$", views.oopsie),
    path(r"^labeldelay$", views.label_with_delay),
    path("", include("django_prometheus.urls")),
]
