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
    page = context.get("page") or context.get("self")
    page_desc = (getattr(page, "search_description", "") or "").strip() if page else ""
    desc = page_desc or getattr(settings, "meta_description", "") or "Миколаївський ліцей №9 — якісна освіта, інноваційні методики та професійні педагоги."
    if desc:
        tags.append(format_html('<meta name="description" content="{}">', desc))
        tags.append(format_html('<meta property="og:description" content="{}">', desc))
        tags.append(format_html('<meta name="twitter:description" content="{}">', desc))

    page_title = getattr(page, "title", "") if page else getattr(settings, "site_name", "Миколаївський ліцей №9")
    if page_title:
        tags.append(format_html('<meta property="og:title" content="{}">', page_title))
        tags.append(format_html('<meta name="twitter:title" content="{}">', page_title))

    tags.append(format_html('<meta property="og:type" content="website">'))
    if request:
        tags.append(format_html('<meta property="og:url" content="{}">', request.build_absolute_uri()))

    if settings.default_og_image:
        og_url = settings.default_og_image.file.url
        tags.extend(
            [
                format_html('<meta property="og:image" content="{}">', og_url),
                format_html('<meta name="twitter:card" content="summary_large_image">'),
                format_html('<meta name="twitter:image" content="{}">', og_url),
            ]
        )
    else:
        emblem_url = request.build_absolute_uri("/static/images/emblem.png")
        tags.extend(
            [
                format_html('<meta property="og:image" content="{}">', emblem_url),
                format_html('<meta name="twitter:card" content="summary">'),
                format_html('<meta name="twitter:image" content="{}">', emblem_url),
            ]
        )

    site_name = getattr(settings, "site_name", "") or "Миколаївський ліцей №9"
    tags.append(format_html('<meta property="og:site_name" content="{}">', site_name))

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
