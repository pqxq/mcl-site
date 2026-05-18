from django import template
from django.utils.html import format_html, format_html_join
from wagtail.models import Site

from core.models import SiteSettings

register = template.Library()


@register.simple_tag(takes_context=True)
def seo_head(context):
    request = context.get("request")
    if request is None:
        return ""

    site = Site.find_for_request(request)
    if site is None:
        return ""

    try:
        settings = SiteSettings.for_site(site)
    except SiteSettings.DoesNotExist:
        return ""
    tags = []

    if settings.meta_description:
        tags.append(format_html('<meta name="description" content="{}">', settings.meta_description))

    if settings.default_og_image:
        og_url = settings.default_og_image.file.url
        tags.extend(
            [
                format_html('<meta property="og:image" content="{}">', og_url),
                format_html('<meta name="twitter:card" content="summary_large_image">'),
                format_html('<meta name="twitter:image" content="{}">', og_url),
            ]
        )

    if settings.site_name:
        tags.append(format_html('<meta property="og:site_name" content="{}">', settings.site_name))

    if settings.google_analytics_id:
        tags.append(
            format_html(
                '<script async src="https://www.googletagmanager.com/gtag/js?id={}"></script>',
                settings.google_analytics_id,
            )
        )
        tags.append(
            format_html(
                """
                <script>
                window.dataLayer = window.dataLayer || [];
                function gtag(){{dataLayer.push(arguments);}}
                gtag('js', new Date());
                gtag('config', '{}');
                </script>
                """,
                settings.google_analytics_id,
            )
        )

    return format_html_join("\n", "{}", ((tag,) for tag in tags))
