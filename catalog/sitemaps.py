from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Category


class StaticViewSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return ['catalog:home', 'catalog:category_list', 'catalog:privacy', 'catalog:terms']

    def location(self, item):
        return reverse(item)


class CategorySitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.9

    def items(self):
        return Category.objects.filter(is_active=True)

    def location(self, obj):
        return reverse('catalog:product_list', kwargs={'category_slug': obj.slug})

    def lastmod(self, obj):
        return obj.created_at
