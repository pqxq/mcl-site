from typing import Optional
from django import template
from core.models import SidebarSection

register = template.Library()


@register.simple_tag
def get_sidebar_sections():
    """Get all sidebar sections with their links"""
    return SidebarSection.objects.prefetch_related('links', 'links__page').all()


@register.simple_tag
def get_sidebar_pages(root_page):
    """
    Get sidebar pages split into system pages and content pages.
    Returns a dict with 'system' and 'content' lists.
    """
    if not root_page:
        return {'system': [], 'content': []}
    
    system_types = ['AboutPage', 'NewsIndexPage', 'StaffIndexPage', 
                    'DocumentsIndexPage', 'ApplicationFormPage']
    
    system_pages = []
    content_pages = []
    
    for page in root_page.get_children().live().in_menu():
        class_name = page.specific_class.__name__
        if class_name in system_types:
            system_pages.append(page)
        else:
            content_pages.append(page)
    
    return {'system': system_pages, 'content': content_pages}


@register.filter
def page_icon(page):
    """Return Bootstrap icon class based on page type"""
    if not page:
        return "bi-file-earmark-text"
    
    class_name = page.specific_class.__name__
    
    icon_map = {
        'HomePage': 'bi-house-door',
        'NewsIndexPage': 'bi-newspaper',
        'NewsPage': 'bi-newspaper',
        'ContentPage': 'bi-file-earmark-text',
        'AboutPage': 'bi-building',
        'StandardPage': 'bi-file-earmark-text',
        'StaffIndexPage': 'bi-people',
        'PersonPage': 'bi-person',
        'DocumentsIndexPage': 'bi-folder2',
        'PublicDocumentPage': 'bi-file-earmark-text',
        'DocumentPage': 'bi-folder-fill',
        'ApplicationFormPage': 'bi-mortarboard',
        'EducationPage': 'bi-book',
        'SchedulePage': 'bi-calendar-week',
    }
    
    return icon_map.get(class_name, 'bi-file-earmark-text')


@register.filter
def is_content_page(page):
    """Check if page is a ContentPage (not a system page)"""
    if not page:
        return False
    class_name = page.specific_class.__name__
    return class_name == 'ContentPage'