from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from catalog.models import Product
from .cart import Cart


@require_POST
def cart_add(request, product_id):
    """
    Add a product to the cart
    """
    from catalog.models import ProductVariant, ProductSize

    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, is_active=True)
    quantity = int(request.POST.get('quantity', 1))

    # Extract and validate variant (color)
    variant_id = request.POST.get('color_id')
    variant = None
    if variant_id:
        variant = get_object_or_404(ProductVariant, id=variant_id, product=product, is_active=True)

    # Extract and validate size
    size_id = request.POST.get('size_id')
    size = None
    if size_id:
        size = get_object_or_404(ProductSize, id=size_id, product=product, is_active=True)

    cart.add(product=product, quantity=quantity, variant=variant, size=size, update_quantity=False)

    return JsonResponse({
        'status': 'success',
        'message': 'Товар добавлен в корзину',
        'cart_total_items': len(cart),
        'cart_total_price': str(cart.get_total_price())
    })


@require_POST
def cart_remove(request, product_id):
    """
    Remove a product from the cart
    """
    from catalog.models import ProductVariant, ProductSize

    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)

    variant_id = request.POST.get('variant_id')
    variant = None
    if variant_id:
        try:
            variant = ProductVariant.objects.get(id=variant_id, product=product)
        except ProductVariant.DoesNotExist:
            pass

    size_id = request.POST.get('size_id')
    size = None
    if size_id:
        try:
            size = ProductSize.objects.get(id=size_id, product=product)
        except ProductSize.DoesNotExist:
            pass

    cart.remove(product, variant=variant, size=size)

    return JsonResponse({
        'status': 'success',
        'message': 'Товар удален из корзины',
        'cart_total_items': len(cart),
        'cart_total_price': str(cart.get_total_price())
    })


@require_POST
def cart_update(request, product_id):
    """
    Update product quantity in the cart
    """
    from catalog.models import ProductVariant, ProductSize

    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))

    variant_id = request.POST.get('variant_id')
    variant = None
    if variant_id:
        try:
            variant = ProductVariant.objects.get(id=variant_id, product=product)
        except ProductVariant.DoesNotExist:
            pass

    size_id = request.POST.get('size_id')
    size = None
    if size_id:
        try:
            size = ProductSize.objects.get(id=size_id, product=product)
        except ProductSize.DoesNotExist:
            pass

    if quantity > 0:
        cart.add(product=product, quantity=quantity, variant=variant, size=size, update_quantity=True)
        message = 'Количество обновлено'
    else:
        cart.remove(product, variant=variant, size=size)
        message = 'Товар удален из корзины'

    return JsonResponse({
        'status': 'success',
        'message': message,
        'cart_total_items': len(cart),
        'cart_total_price': str(cart.get_total_price())
    })


def cart_detail(request):
    """
    Return cart details as JSON
    """
    cart = Cart(request)
    return JsonResponse(cart.get_cart_data())


def cart_page(request):
    """
    Display cart page
    """
    cart = Cart(request)
    return render(request, 'cart/cart.html', {'cart': cart})
