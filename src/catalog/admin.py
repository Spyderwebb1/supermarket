from django.contrib import admin
from .models import Item, Category, OrderItem, Order
# Register your models here.

admin.site.register(Item)
admin.site.register(Category)


class OrderItemInline(admin.TabularInline):
    """Defines format of inline orderitem insertion (used in OrderAdmin)"""
    model = OrderItem
    fields = ('item','quantity',)
    readonly_fields = ('item','quantity',)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id','ordered', 'fulfilled', 'user')
    inlines = [OrderItemInline]

admin.site.register(Order, OrderAdmin)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Administration object for OrderItem models.
    Defines:
     - fields to be displayed in list view (list_display)
     - filters that will be displayed in sidebar (list_filter)
     - grouping of fields into sections (fieldsets)
    """
    list_display = ('item', 'quantity')