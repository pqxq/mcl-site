from django.utils.html import escape
from wagtail import hooks
from wagtail.admin.rich_text.converters.html_to_contentstate import InlineStyleElementHandler
from wagtail.admin.rich_text.editors.draftail.features import InlineStyleFeature
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
    Register 'underline' as a Draftail inline style feature with proper
    editor plugin and HTML converter.
    """
    feature_name = "underline"
    type_ = "UNDERLINE"

    control = {
        "type": type_,
        "label": "U",
        "description": "Underline",
        "style": {"textDecoration": "underline"},
    }

    features.register_editor_plugin(
        "draftail", feature_name, InlineStyleFeature(control)
    )

    db_conversion = {
        "from_database_format": {"u[{}]": InlineStyleElementHandler(type_)},
        "to_database_format": {"style_map": {type_: "u"}},
    }
    features.register_converter_rule("contentstate", feature_name, db_conversion)

    if feature_name not in features.default_features:
        features.default_features.append(feature_name)


@hooks.register("register_rich_text_features")
def register_strikethrough_feature(features):
    """
    Register 'strikethrough' as a Draftail inline style feature with proper
    editor plugin and HTML converter.
    """
    feature_name = "strikethrough"
    type_ = "STRIKETHROUGH"

    control = {
        "type": type_,
        "label": "S",
        "description": "Strikethrough",
        "style": {"textDecoration": "line-through"},
    }

    features.register_editor_plugin(
        "draftail", feature_name, InlineStyleFeature(control)
    )

    db_conversion = {
        "from_database_format": {"s[{}]": InlineStyleElementHandler(type_)},
        "to_database_format": {"style_map": {type_: "s"}},
    }
    features.register_converter_rule("contentstate", feature_name, db_conversion)

    if feature_name not in features.default_features:
        features.default_features.append(feature_name)
