from django import template
from core.models import SidebarSection

register = template.Library()

SYSTEM_PAGE_TYPES = {
    "AboutPage",
    "NewsIndexPage",
    "StaffIndexPage",
    "DocumentsIndexPage",
    "ApplicationFormPage",
    "GalleryIndexPage",
}

PAGE_ICON_MAP = {
    "HomePage": "bi-house-door",
    "NewsIndexPage": "bi-newspaper",
    "NewsPage": "bi-newspaper",
    "ContentPage": "bi-file-earmark-text",
    "AboutPage": "bi-building",
    "StandardPage": "bi-file-earmark-text",
    "StaffIndexPage": "bi-people",
    "PersonPage": "bi-person",
    "DocumentsIndexPage": "bi-folder2",
    "PublicDocumentPage": "bi-file-earmark-text",
    "DocumentPage": "bi-folder-fill",
    "ApplicationFormPage": "bi-mortarboard",
    "EducationPage": "bi-book",
    "SchedulePage": "bi-calendar-week",
    "GalleryIndexPage": "bi-images",
    "GalleryAlbumPage": "bi-images",
}


@register.simple_tag
def get_sidebar_sections():
    """Get all sidebar sections with their links"""
    return SidebarSection.objects.prefetch_related("links", "links__page")


@register.simple_tag
def get_sidebar_pages(root_page):
    """
    Get sidebar pages split into system pages and content pages.
    Returns a dict with 'system' and 'content' lists.
    """
    if not root_page:
        return {"system": [], "content": []}

    system_pages = []
    content_pages = []

    for page in root_page.get_children().live().in_menu().specific():
        class_name = page.__class__.__name__
        if class_name in SYSTEM_PAGE_TYPES:
            system_pages.append(page)
        else:
            content_pages.append(page)

    return {"system": system_pages, "content": content_pages}


@register.filter
def page_icon(page):
    """Return Bootstrap icon class based on page type"""
    if not page:
        return "bi-file-earmark-text"

    class_name = page.specific_class.__name__
    return PAGE_ICON_MAP.get(class_name, "bi-file-earmark-text")


@register.filter
def is_content_page(page):
    """Check if page is a ContentPage (not a system page)"""
    if not page:
        return False
    return page.specific_class.__name__ == "ContentPage"
