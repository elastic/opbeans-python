from django.contrib import admin
from opbeans import models


class OrderLineInlineAdmin(admin.TabularInline):
    model = models.OrderLine


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    select_related = ['customer']
    list_display = ['pk', 'customer', 'created_at']
    date_hierarchy = 'created_at'
    inlines = [OrderLineInlineAdmin]


admin.site.register(models.Customer)
admin.site.register(models.Product)
admin.site.register(models.ProductType)
