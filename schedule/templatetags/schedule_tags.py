from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get item from dictionary by key in template"""
    if dictionary is None:
        return None
    return dictionary.get(key)
