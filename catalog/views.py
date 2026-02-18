from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import Category, Product


class CategoryListView(ListView):
    """Display list of all active categories"""
    model = Category
    template_name = 'catalog/category_list.html'
    context_object_name = 'categories'
    queryset = Category.objects.filter(is_active=True)


class ProductListView(ListView):
    """Display products by category with pagination"""
    model = Product
    template_name = 'catalog/product_list.html'
    context_object_name = 'products'
    paginate_by = 9

    def get_queryset(self):
        """Filter products by category and active status"""
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_active=True
        )
        return Product.objects.filter(
            category=self.category,
            is_active=True
        )

    def get_context_data(self, **kwargs):
        """Add category to context"""
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['categories'] = Category.objects.filter(is_active=True)
        return context


def product_detail_json(request, product_slug):
    """
    Return product details as JSON for modal window
    Includes multiple gallery images and related products
    """
    product = get_object_or_404(
        Product.objects.prefetch_related('variants', 'gallery_images__variant'),
        slug=product_slug,
        is_active=True
    )

    # Get related products from the same category
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id)[:4]

    # Get all gallery images for this product
    gallery_images = product.gallery_images.all()

    # Build product data
    product_data = {
        'id': product.id,
        'name': product.name,
        'slug': product.slug,
        'description': product.description,
        'price': str(product.price),
        'status': product.get_status_display(),
        'status_code': product.status,
        'colors': [
            {
                'id': variant.id,
                'name': variant.name,
                'size': variant.size,
                'display_name': variant.get_display_name(),
                'quantity': variant.quantity,
                'is_active': variant.is_active
            }
            for variant in product.get_available_variants()
        ],
        'total_quantity': product.get_total_quantity(),
        'image': product.get_primary_image_url(),
        'gallery_images': [
            {
                'url': img.image.url,
                'alt_text': img.alt_text or product.name,
                'is_primary': img.is_primary,
                'order': img.order,
                'variant_id': img.variant_id,
                'variant_name': img.variant.get_display_name() if img.variant else None
            }
            for img in gallery_images
        ],
        'category': {
            'name': product.category.name,
            'slug': product.category.slug
        },
        'related_products': [
            {
                'id': p.id,
                'name': p.name,
                'slug': p.slug,
                'price': str(p.price),
                'image': p.get_primary_image_url()
            }
            for p in related_products
        ]
    }

    return JsonResponse(product_data)


def home_view(request):
    """
    Home page view showing featured products
    """
    categories = Category.objects.filter(is_active=True)
    featured_products = Product.objects.filter(is_active=True)[:8]

    context = {
        'categories': categories,
        'featured_products': featured_products
    }
    return render(request, 'catalog/home.html', context)
