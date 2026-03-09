from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display
from .models import Order, OrderItem


class OrderItemInline(TabularInline):
    """Inline admin for OrderItem"""
    model = OrderItem
    # raw_id_fields = ['product']
    extra = 0
    readonly_fields = ['price', 'quantity', 'variant_display_name', 'size_display_name']
    fields = ['product', 'variant_display_name', 'size_display_name', 'price', 'quantity']


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    """Admin configuration for Order model"""
    list_display = [
        'id',
        'full_name',
        'email',
        'phone',
        'city',
        'total_price',
        'status',
        'created_at'
    ]
    list_filter = [
        'status',
        'contact_method',
        'created_at',
        'region',
        'city'
    ]
    search_fields = [
        'full_name',
        'email',
        'phone',
        'city',
        'street'
    ]
    list_editable = ['status']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at', 'total_price']
    inlines = [OrderItemInline]
    compressed_fields = True
    list_filter_submit = True
    list_fullwidth = True

    fieldsets = (
        ('Customer information', {
            'fields': ('full_name', 'email', 'phone', 'contact_method')
        }),
        ('Delivery address', {
            'fields': ('region', 'city', 'street', 'house', 'building', 'apartment')
        }),
        ('Order information', {
            'fields': ('total_price', 'status', 'created_at', 'updated_at')
        }),
    )


# @admin.register(OrderItem)
# class OrderItemAdmin(ModelAdmin):
#     """Admin configuration for OrderItem model"""
#     list_display = ['order', 'product', 'price', 'quantity', 'get_total_price']
#     list_filter = ['order__created_at']
#     raw_id_fields = ['order', 'product']
#     readonly_fields = ['get_total_price']
#     compressed_fields = True
#     list_filter_submit = True

#     @display(description='Total cost')
#     def get_total_price(self, obj):
#         """Display total price for this order item"""
#         return obj.get_total_price()
