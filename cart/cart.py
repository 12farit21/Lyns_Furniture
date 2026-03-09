from decimal import Decimal
from django.conf import settings
from catalog.models import Product


class Cart:
    """
    Session-based shopping cart
    """

    def __init__(self, request):
        """
        Initialize the cart
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # Save an empty cart in the session
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, update_quantity=False, variant=None, size=None):
        """
        Add a product to the cart or update its quantity
        """
        # Generate composite key for color+size-specific items
        variant_part = str(variant.id) if variant else ''
        size_part = str(size.id) if size else ''
        cart_key = f"{product.id}_{variant_part}_{size_part}"

        if cart_key not in self.cart:
            self.cart[cart_key] = {
                'quantity': 0,
                'price': str(product.price),
                'variant_id': variant.id if variant else None,
                'size_id': size.id if size else None,
            }

        if update_quantity:
            self.cart[cart_key]['quantity'] = quantity
        else:
            self.cart[cart_key]['quantity'] += quantity

        self.save()

    def save(self):
        """
        Mark the session as modified to make sure it gets saved
        """
        self.session.modified = True

    def remove(self, product, variant=None, size=None):
        """
        Remove a product from the cart
        """
        variant_part = str(variant.id) if variant else ''
        size_part = str(size.id) if size else ''
        cart_key = f"{product.id}_{variant_part}_{size_part}"

        if cart_key in self.cart:
            del self.cart[cart_key]
            self.save()

    def __iter__(self):
        """
        Iterate over the items in the cart and get the products from the database
        """
        from catalog.models import ProductVariant, ProductSize

        # Parse cart keys to extract product IDs
        product_ids = []
        for key in self.cart.keys():
            product_id = key.split('_')[0]  # Get product ID from composite key
            product_ids.append(product_id)

        # Get the product objects
        products = Product.objects.filter(id__in=product_ids)
        products_dict = {str(p.id): p for p in products}

        cart = self.cart.copy()
        for cart_key, item_data in cart.items():
            product_id = cart_key.split('_')[0]

            if product_id not in products_dict:
                continue  # Skip if product deleted

            product = products_dict[product_id]
            item_data['product'] = product

            # Add variant (color) object if variant_id exists
            variant_id = item_data.get('variant_id')
            if variant_id:
                try:
                    variant = ProductVariant.objects.get(id=variant_id, product=product)
                    item_data['variant'] = variant
                except ProductVariant.DoesNotExist:
                    item_data['variant'] = None
            else:
                item_data['variant'] = None

            # Add size object if size_id exists
            size_id = item_data.get('size_id')
            if size_id:
                try:
                    size = ProductSize.objects.get(id=size_id, product=product)
                    item_data['size'] = size
                except ProductSize.DoesNotExist:
                    item_data['size'] = None
            else:
                item_data['size'] = None

            item_data['price'] = Decimal(item_data['price'])
            item_data['total_price'] = item_data['price'] * item_data['quantity']
            item_data['image_url'] = self._get_variant_image_url(product, item_data['variant'])
            yield item_data

    def __len__(self):
        """
        Count all items in the cart
        """
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """
        Calculate the total price of all items in the cart
        """
        return sum(
            Decimal(item['price']) * item['quantity']
            for item in self.cart.values()
        )

    def clear(self):
        """
        Remove cart from session
        """
        del self.session[settings.CART_SESSION_ID]
        self.save()

    def get_cart_data(self):
        """
        Get cart data as a list for JSON responses
        """
        items = []
        for item in self:
            product = item['product']
            variant = item.get('variant')

            # Get variant-specific image or fallback to product image
            image_url = self._get_variant_image_url(product, variant)

            size = item.get('size')
            items.append({
                'product_id': product.id,
                'product_name': product.name,
                'product_image': image_url,
                'quantity': item['quantity'],
                'price': str(item['price']),
                'total_price': str(item['total_price']),
                'variant_id': variant.id if variant else None,
                'variant_display_name': variant.get_display_name() if variant else None,
                'size_id': size.id if size else None,
                'size_display_name': size.get_display_name() if size else None,
            })

        return {
            'items': items,
            'total_items': len(self),
            'total_price': str(self.get_total_price())
        }

    def _get_variant_image_url(self, product, variant):
        """
        Get the correct image URL for a product variant.
        Returns variant-specific image (lowest order) or product primary image.
        """
        from catalog.models import ProductGallery

        if variant:
            # Get variant-specific image with lowest order value
            variant_image = ProductGallery.objects.filter(
                product=product,
                variant=variant
            ).order_by('order', 'created_at').first()

            if variant_image:
                return variant_image.image.url

        # Fallback to product's primary/default image
        return product.get_image_url()
