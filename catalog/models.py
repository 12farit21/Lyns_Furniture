from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    """Product category model"""
    name = models.CharField(
        max_length=200,
        verbose_name=_('Name')
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
        verbose_name=_('Image')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Active')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created at')
    )

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
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
    BEST_SELLER = 'best_seller'
    NEW_ARRIVAL = 'new_arrival'
    HOT_DEAL = 'hot_deal'
    LIMITED_STOCK = 'limited_stock'
    EXCLUSIVE = 'exclusive'

    STATUS_CHOICES = [
        (IN_STOCK, _('In Stock')),
        (ON_ORDER, _('On Order')),
        (BEST_SELLER, _('Best Seller')),
        (NEW_ARRIVAL, _('New Arrival')),
        (HOT_DEAL, _('Hot Deal')),
        (LIMITED_STOCK, _('Limited Stock')),
        (EXCLUSIVE, _("Exclusive to Lyn's Furniture")),
    ]

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name=_('Category')
    )
    name = models.CharField(
        max_length=200,
        verbose_name=_('Name')
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name=_('URL')
    )
    description = models.TextField(
        verbose_name=_('Description')
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Sale price')
    )
    price_before_discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name=_('Price before discount')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=IN_STOCK,
        verbose_name=_('Status')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Active')
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name=_('Featured')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created at')
    )

    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
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

    def has_stock(self):
        """Check if product has any active variants"""
        return self.variants.filter(is_active=True).exists()

    def get_primary_variant(self):
        """Return the first active variant or None"""
        return self.variants.filter(is_active=True).first()

    def get_discount_percent(self):
        """Return discount percentage rounded to integer, or None"""
        if self.price_before_discount and self.price_before_discount > self.price:
            discount = (self.price_before_discount - self.price) / self.price_before_discount * 100
            return round(discount)
        return None


class ProductVariant(models.Model):
    """Product variant model with color and size support"""

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='variants',
        verbose_name=_('Product')
    )
    name = models.CharField(
        max_length=100,
        verbose_name=_('Color')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Active')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created at')
    )

    class Meta:
        verbose_name = _('Product color')
        verbose_name_plural = _('Product colors')
        ordering = ['name']

    def __str__(self):
        return f"{self.product.name} - {self.name}"

    def get_display_name(self):
        return self.name or ''

    def clean(self):
        from django.core.exceptions import ValidationError

        if not self.name:
            raise ValidationError(_('The Color field is required'))

        qs = ProductVariant.objects.filter(product=self.product)
        if self.pk:
            qs = qs.exclude(pk=self.pk)

        if qs.filter(name=self.name).exists():
            raise ValidationError(_('This color already exists'))


class ProductGallery(models.Model):
    """Product image gallery model"""

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='gallery_images',
        verbose_name=_('Product')
    )
    variant = models.ForeignKey(
        'ProductVariant',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='images',
        verbose_name=_('Color')
    )
    image = models.ImageField(
        upload_to='products/%Y/%m/%d/',
        verbose_name=_('Image')
    )
    alt_text = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Alt text')
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Order')
    )
    is_primary = models.BooleanField(
        default=False,
        verbose_name=_('Primary image')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Uploaded at')
    )

    class Meta:
        verbose_name = _('Product image')
        verbose_name_plural = _('Product images')
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.product.name} - Image {self.order}"

    def save(self, *args, **kwargs):
        # If this is marked as primary, unmark all other images for this product
        if self.is_primary:
            ProductGallery.objects.filter(product=self.product).exclude(id=self.id).update(is_primary=False)
        super().save(*args, **kwargs)


class ProductSize(models.Model):
    """Product size model (Twin, Full, Queen, King, etc.)"""

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='sizes',
        verbose_name=_('Product')
    )
    name = models.CharField(
        max_length=100,
        verbose_name=_('Size')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Active')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created at')
    )

    class Meta:
        verbose_name = _('Product size')
        verbose_name_plural = _('Product sizes')
        ordering = ['name']

    def __str__(self):
        return f"{self.product.name} - {self.name}"

    def get_display_name(self):
        return self.name or ''

    def clean(self):
        from django.core.exceptions import ValidationError

        if not self.name:
            raise ValidationError(_('The Size field is required'))

        qs = ProductSize.objects.filter(product=self.product)
        if self.pk:
            qs = qs.exclude(pk=self.pk)

        if qs.filter(name=self.name).exists():
            raise ValidationError(_('This size already exists'))


class ContactMessage(models.Model):
    """Contact form submission"""
    first_name = models.CharField(max_length=100, verbose_name=_('First Name'))
    last_name = models.CharField(max_length=100, verbose_name=_('Last Name'))
    email = models.EmailField(verbose_name=_('Email'))
    phone = models.CharField(max_length=50, blank=True, verbose_name=_('Phone'))
    message = models.TextField(verbose_name=_('Message'))
    is_read = models.BooleanField(default=False, verbose_name=_('Read'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Received at'))

    class Meta:
        verbose_name = _('Contact Message')
        verbose_name_plural = _('Contact Messages')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name} — {self.email}"
