from django.utils.html import escape
from wagtail import hooks
from wagtail.rich_text import LinkHandler


class ExternalLinkHandler(LinkHandler):
    identifier = "external"

    @classmethod
    def expand_db_attributes(cls, attrs: dict) -> str:
        href = attrs.get("href", "")
        extra_attrs = []
        for k, v in attrs.items():
            if k not in ("href", "target", "rel", "linktype"):
                extra_attrs.append(f'{escape(k)}="{escape(v)}"')
        extra_str = f" {' '.join(extra_attrs)}" if extra_attrs else ""
        return f'<a href="{escape(href)}" target="_blank" rel="noopener noreferrer"{extra_str}>'


@hooks.register("register_rich_text_features")
def register_external_link_feature(features):
    """
    Ensure external links in RichText open in a new tab with security attributes.
    """
    features.register_link_type(ExternalLinkHandler)


@hooks.register("register_rich_text_features")
def register_underline_feature(features):
    """
    Ensure 'underline' is registered in default rich text features so that all
    RichTextField and RichTextBlock instances in the Wagtail Admin panel have access
    to the Underline formatting option.
    """
    if "underline" not in features.default_features:
        features.default_features.append("underline")

