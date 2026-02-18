from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    """Product category model"""
    name = models.CharField(
        max_length=200,
        verbose_name=_('Название')
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name=_('URL')
    )
    image = models.ImageField(
        upload_to='categories/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name=_('Изображение')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Активна')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата создания')
    )

    class Meta:
        verbose_name = _('Категория')
        verbose_name_plural = _('Категории')
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    """Product model"""

    # Status choices
    IN_STOCK = 'in_stock'
    ON_ORDER = 'on_order'

    STATUS_CHOICES = [
        (IN_STOCK, _('В наличии')),
        (ON_ORDER, _('Под заказ')),
    ]

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name=_('Категория')
    )
    name = models.CharField(
        max_length=200,
        verbose_name=_('Название')
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name=_('URL')
    )
    description = models.TextField(
        verbose_name=_('Описание')
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Цена (тенге)')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=IN_STOCK,
        verbose_name=_('Статус')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Активен')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата создания')
    )

    class Meta:
        verbose_name = _('Товар')
        verbose_name_plural = _('Товары')
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_primary_image_url(self):
        """Return primary image URL or first image or placeholder"""
        primary_image = self.gallery_images.filter(is_primary=True).first()
        if primary_image:
            return primary_image.image.url

        first_image = self.gallery_images.first()
        if first_image:
            return first_image.image.url

        return '/static/images/placeholder.jpg'

    def get_all_images(self):
        """Return all gallery images ordered"""
        return self.gallery_images.all()

    def get_image_url(self):
        """Backward compatibility - redirects to get_primary_image_url"""
        return self.get_primary_image_url()

    def get_available_variants(self):
        """Return all active variants for this product"""
        return self.variants.filter(is_active=True)

    def get_total_quantity(self):
        """Return total quantity across all variants"""
        return self.variants.filter(is_active=True).aggregate(
            total=models.Sum('quantity')
        )['total'] or 0

    def has_stock(self):
        """Check if product has any stock available"""
        return self.get_total_quantity() > 0

    def get_primary_variant(self):
        """Return the first active variant or None"""
        return self.variants.filter(is_active=True).first()


class ProductVariant(models.Model):
    """Product variant model with color and size support"""

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='variants',
        verbose_name=_('Товар')
    )
    name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Цвет')
    )
    size = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Размер')
    )
    quantity = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Количество')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Активен')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата создания')
    )

    class Meta:
        verbose_name = _('Цвет/Размер товара')
        verbose_name_plural = _('Цвета/Размеры товара')
        ordering = ['name', 'size']

    def __str__(self):
        variant_display = self.get_display_name() or _('Без варианта')
        return f"{self.product.name} - {variant_display}"

    def get_display_name(self):
        """Return display name showing only filled values"""
        parts = []
        if self.name:
            parts.append(self.name)
        if self.size:
            parts.append(self.size)
        return ' '.join(parts) if parts else ''

    def clean(self):
        """Validate that at least one of name or size is filled"""
        from django.core.exceptions import ValidationError

        if not self.name and not self.size:
            raise ValidationError(
                _('Необходимо заполнить хотя бы одно поле: Цвет или Размер')
            )

        # Check for duplicate combinations
        qs = ProductVariant.objects.filter(product=self.product)
        if self.pk:
            qs = qs.exclude(pk=self.pk)

        if self.name and self.size:
            if qs.filter(name=self.name, size=self.size).exists():
                raise ValidationError(
                    _('Комбинация цвета и размера уже существует')
                )
        elif self.name:
            if qs.filter(name=self.name, size__isnull=True).exists():
                raise ValidationError(_('Этот цвет уже существует'))
        elif self.size:
            if qs.filter(size=self.size, name__isnull=True).exists():
                raise ValidationError(_('Этот размер уже существует'))


class ProductGallery(models.Model):
    """Product image gallery model"""

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='gallery_images',
        verbose_name=_('Товар')
    )
    variant = models.ForeignKey(
        'ProductVariant',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='images',
        verbose_name=_('Цвет/Размер')
    )
    image = models.ImageField(
        upload_to='products/%Y/%m/%d/',
        verbose_name=_('Изображение')
    )
    alt_text = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Альтернативный текст')
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Порядок')
    )
    is_primary = models.BooleanField(
        default=False,
        verbose_name=_('Основное изображение')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата загрузки')
    )

    class Meta:
        verbose_name = _('Изображение товара')
        verbose_name_plural = _('Изображения товара')
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.product.name} - Image {self.order}"

    def save(self, *args, **kwargs):
        # If this is marked as primary, unmark all other images for this product
        if self.is_primary:
            ProductGallery.objects.filter(product=self.product).exclude(id=self.id).update(is_primary=False)
        super().save(*args, **kwargs)
