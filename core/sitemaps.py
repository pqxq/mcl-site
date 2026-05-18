from django.contrib.sitemaps import Sitemap
from wagtail.models import Page


class WagtailPageSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Page.objects.live().public().specific().order_by("-first_published_at")

    def lastmod(self, obj):
        return obj.latest_revision_created_at or obj.last_published_at or obj.first_published_at
