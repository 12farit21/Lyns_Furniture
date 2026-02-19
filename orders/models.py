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
        (NEW, _('Новый')),
        (PROCESSING, _('В обработке')),
        (COMPLETED, _('Завершен')),
    ]

    # Contact method choices
    WHATSAPP = 'whatsapp'
    PHONE_CALL = 'phone_call'
    EMAIL = 'email'

    CONTACT_METHOD_CHOICES = [
        (WHATSAPP, _('WhatsApp')),
        (PHONE_CALL, _('Телефонный звонок')),
        (EMAIL, _('Email')),
    ]

    # Customer information
    full_name = models.CharField(
        max_length=200,
        verbose_name=_('ФИО')
    )
    email = models.EmailField(
        verbose_name=_('Email')
    )
    phone = models.CharField(
        max_length=20,
        verbose_name=_('Телефон')
    )
    contact_method = models.CharField(
        max_length=20,
        choices=CONTACT_METHOD_CHOICES,
        default=WHATSAPP,
        verbose_name=_('Способ связи')
    )

    # Delivery address
    region = models.CharField(
        max_length=100,
        verbose_name=_('Область')
    )
    city = models.CharField(
        max_length=100,
        verbose_name=_('Город')
    )
    street = models.CharField(
        max_length=200,
        verbose_name=_('Улица')
    )
    house = models.CharField(
        max_length=20,
        verbose_name=_('Дом')
    )
    building = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_('Корпус')
    )
    apartment = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_('Квартира')
    )

    # Order details
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Общая сумма (тенге)')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=NEW,
        verbose_name=_('Статус')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата создания')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Дата обновления')
    )

    class Meta:
        verbose_name = _('Заказ')
        verbose_name_plural = _('Заказы')
        ordering = ['-created_at']

    def __str__(self):
        return f'Заказ №{self.pk} от {self.created_at.strftime("%d.%m.%Y")}'

    def get_full_address(self):
        """Return full delivery address"""
        address_parts = [
            self.region,
            self.city,
            self.street,
            f'д. {self.house}'
        ]
        if self.building:
            address_parts.append(f'корп. {self.building}')
        if self.apartment:
            address_parts.append(f'кв. {self.apartment}')
        return ', '.join(address_parts)


class OrderItem(models.Model):
    """Order item model - products in the order"""

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('Заказ')
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        verbose_name=_('Товар')
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Цена (тенге)')
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name=_('Количество')
    )
    variant_display_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Вариант (Цвет/Размер)')
    )

    class Meta:
        verbose_name = _('Товар в заказе')
        verbose_name_plural = _('Товары в заказе')

    def __str__(self):
        if self.variant_display_name:
            return f'{self.product.name} ({self.variant_display_name}) x {self.quantity}'
        return f'{self.product.name} x {self.quantity}'

    def get_total_price(self):
        """Return total price for this order item"""
        return self.price * self.quantity
