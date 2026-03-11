from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView
from django.urls import reverse_lazy
from cart.cart import Cart
from .forms import OrderCreateForm
from .models import Order, OrderItem


def order_create(request):
    """
    Create an order from cart contents
    """
    cart = Cart(request)

    # Check if cart is empty
    if len(cart) == 0:
        return redirect('catalog:home')

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            # Create order
            order = form.save(commit=False)
            order.total_price = cart.get_total_price()
            order.save()

            # Create order items
            for item in cart:
                variant = item.get('variant')
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity'],
                    variant_display_name=variant.get_display_name() if variant else '',
                    size_display_name='',
                )

            # Clear the cart
            cart.clear()

            # Redirect to success page
            return redirect('orders:order_success', order_id=order.id)
    else:
        form = OrderCreateForm()

    context = {
        'form': form,
        'cart': cart
    }
    return render(request, 'orders/order_create.html', context)


def order_success(request, order_id):
    """
    Order success page
    """
    order = get_object_or_404(Order, pk=order_id)
    return render(request, 'orders/order_success.html', {'order': order})
