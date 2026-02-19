from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display
from .models import Category, Product, ProductGallery, ProductVariant


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    """Admin configuration for Category model"""
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active']
    # date_hierarchy = 'created_at'
    compressed_fields = True
    list_filter_submit = True

    def get_fields(self, request, obj=None):
        """Hide slug field for Manager group"""
        fields = super().get_fields(request, obj)
        if request.user.groups.filter(name='Manager').exists():
            # Convert to list and remove slug field
            fields = [f for f in fields if f != 'slug']
        return fields

    def get_prepopulated_fields(self, request, obj=None):
        """Remove prepopulated_fields for slug if user is in Manager group"""
        if request.user.groups.filter(name='Manager').exists():
            return {}
        return super().get_prepopulated_fields(request, obj)


class ProductVariantInline(TabularInline):
    """Inline admin for product variants (color/size)"""
    model = ProductVariant
    extra = 0
    fields = ['name', 'is_active']


class ProductGalleryInline(TabularInline):
    """Inline admin for product gallery images"""
    model = ProductGallery
    extra = 0
    fields = ['image', 'variant', 'order', 'is_primary']
    # readonly_fields = ['image_preview']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filter variant choices to show only variants of the current product"""
        if db_field.name == "variant":
            # Get product ID from URL
            product_id = request.resolver_match.kwargs.get('object_id')
            if product_id:
                kwargs["queryset"] = ProductVariant.objects.filter(product_id=product_id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    @display(description=_('Превью'))
    def image_preview(self, obj):
        """Display thumbnail preview in admin"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 80px; max-width: 80px; '
                'object-fit: cover; border-radius: 4px;" />',
                obj.image.url
            )
        return '-'


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    """Admin configuration for Product model"""
    list_display = [
        'name',
        'category',
        'price',
        'price_before_discount',
        'status',
        'color_count',
        'is_active',
        'created_at'
    ]
    list_filter = [
        'category',
        'status',
        'is_active',
        'created_at'
    ]
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['price', 'price_before_discount', 'status', 'is_active']
    # date_hierarchy = 'created_at'
    readonly_fields = ['created_at']
    inlines = [ProductVariantInline, ProductGalleryInline]
    compressed_fields = True
    list_filter_submit = True
    list_fullwidth = True

    fieldsets = (
        ('Основная информация', {
            'fields': ('category', 'name', 'slug', 'description')
        }),
        ('Цена и статус', {
            'fields': ('price', 'price_before_discount', 'status')
        }),
        # ('Настройки', {
        #     'fields': ('is_active', 'created_at')
        # }),
    )

    def get_fieldsets(self, request, obj=None):
        """Hide slug field for all users"""
        fieldsets = super().get_fieldsets(request, obj)
        modified_fieldsets = []
        for name, data in fieldsets:
            if name == 'Основная информация':
                fields = tuple(f for f in data['fields'] if f != 'slug')
                modified_data = data.copy()
                modified_data['fields'] = fields
                modified_fieldsets.append((name, modified_data))
            else:
                modified_fieldsets.append((name, data))
        return modified_fieldsets

    def get_prepopulated_fields(self, _request, _obj=None):
        return {}

    @display(description=_('Варианты'))
    def color_count(self, obj):
        """Display count of active variants"""
        count = obj.variants.filter(is_active=True).count()
        if count == 0:
            return format_html('<span style="color: var(--color-error);">0</span>')
        return count


# @admin.register(ProductGallery)
# class ProductGalleryAdmin(ModelAdmin):
#     """Admin for managing gallery images directly"""
#     list_display = ['product', 'image_preview', 'order', 'is_primary', 'created_at']
#     list_filter = ['is_primary', 'created_at']
#     search_fields = ['product__name', 'alt_text']
#     raw_id_fields = ['product']
#     list_editable = ['order', 'is_primary']
#     readonly_fields = ['image_preview', 'created_at']
#     compressed_fields = True
#     list_filter_submit = True

#     @display(description=_('Превью'))
#     def image_preview(self, obj):
#         """Display thumbnail preview in admin"""
#         if obj.image:
#             return format_html(
#                 '<img src="{}" style="max-height: 60px; max-width: 60px; '
#                 'object-fit: cover; border-radius: 4px;" />',
#                 obj.image.url
#             )
#         return '-'
