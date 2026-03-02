from django.db import models
from django.utils.translation import gettext_lazy as _
from catalog.models import Product


class Order(models.Model):
    """Order model"""

    # Status choices
    NEW = 'new'
    PROCESSING = 'processing'
    COMPLETED = 'completed'

    STATUS_CHOICES = [
        (NEW, _('New')),
        (PROCESSING, _('Processing')),
        (COMPLETED, _('Completed')),
    ]

    # Contact method choices
    WHATSAPP = 'whatsapp'
    PHONE_CALL = 'phone_call'
    EMAIL = 'email'

    CONTACT_METHOD_CHOICES = [
        (WHATSAPP, _('WhatsApp')),
        (PHONE_CALL, _('Phone call')),
        (EMAIL, _('Email')),
    ]

    # Customer information
    full_name = models.CharField(
        max_length=200,
        verbose_name=_('Full name')
    )
    email = models.EmailField(
        verbose_name=_('Email')
    )
    phone = models.CharField(
        max_length=20,
        verbose_name=_('Phone')
    )
    contact_method = models.CharField(
        max_length=20,
        choices=CONTACT_METHOD_CHOICES,
        default=WHATSAPP,
        verbose_name=_('Contact method')
    )

    # Delivery address
    region = models.CharField(
        max_length=100,
        verbose_name=_('Region')
    )
    city = models.CharField(
        max_length=100,
        verbose_name=_('City')
    )
    street = models.CharField(
        max_length=200,
        verbose_name=_('Street')
    )
    house = models.CharField(
        max_length=20,
        verbose_name=_('House')
    )
    building = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_('Building')
    )
    apartment = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_('Apartment')
    )

    # Order details
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Total amount')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=NEW,
        verbose_name=_('Status')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created at')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated at')
    )

    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')
        ordering = ['-created_at']

    def __str__(self):
        return f'Order #{self.pk} from {self.created_at.strftime("%d.%m.%Y")}'

    def get_full_address(self):
        """Return full delivery address"""
        address_parts = [
            self.region,
            self.city,
            self.street,
            f'house {self.house}'
        ]
        if self.building:
            address_parts.append(f'bldg. {self.building}')
        if self.apartment:
            address_parts.append(f'apt. {self.apartment}')
        return ', '.join(address_parts)


class OrderItem(models.Model):
    """Order item model - products in the order"""

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('Order')
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        verbose_name=_('Product')
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Price')
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name=_('Quantity')
    )
    variant_display_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Color')
    )

    class Meta:
        verbose_name = _('Order item')
        verbose_name_plural = _('Order items')

    def __str__(self):
        if self.variant_display_name:
            return f'{self.product.name} ({self.variant_display_name}) x {self.quantity}'
        return f'{self.product.name} x {self.quantity}'

    def get_total_price(self):
        """Return total price for this order item"""
        return self.price * self.quantity
