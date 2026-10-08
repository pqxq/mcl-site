from wagtail.contrib.sitemaps import Sitemap
from wagtail.models import Page


class WagtailPageSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def location(self, obj):
        if hasattr(obj, "get_full_url"):
            try:
                url = obj.get_full_url(self.request)
                if url:
                    return url
            except Exception:
                pass
        return getattr(obj, "url", None) or "/"

    def lastmod(self, obj):
        return (
            getattr(obj, "latest_revision_created_at", None)
            or getattr(obj, "last_published_at", None)
            or getattr(obj, "first_published_at", None)
        )

