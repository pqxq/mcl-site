from wagtail import hooks


@hooks.register("register_rich_text_features")
def register_underline_feature(features):
    """
    Ensure 'underline' is registered in default rich text features so that all
    RichTextField and RichTextBlock instances in the Wagtail Admin panel have access
    to the Underline formatting option.
    """
    if "underline" not in features.default_features:
        features.default_features.append("underline")
