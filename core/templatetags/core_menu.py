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
    "StaffIndexPage": "bi-people",
    "PersonPage": "bi-person",
    "DocumentsIndexPage": "bi-folder2",
    "PublicDocumentPage": "bi-file-earmark-text",
    "ApplicationFormPage": "bi-mortarboard",
    "SchedulePage": "bi-calendar-week",
    "GalleryIndexPage": "bi-images",
    "GalleryAlbumPage": "bi-images",
}


@register.simple_tag(takes_context=True)
def get_sidebar_sections(context):
    """Get all sidebar sections with their valid live links, annotating active state based on request/page"""
    request = context.get("request")
    current_path = request.path if request else ""
    current_page = context.get("page") or context.get("self")

    sections = SidebarSection.objects.prefetch_related("links", "links__page").all()
    result = []

    norm_current_path = current_path.rstrip("/") if current_path != "/" else "/"

    for section in sections:
        valid_links = section.valid_links
        if not valid_links:
            continue

        section_has_active = False
        for link in valid_links:
            link_is_active = False
            link_href = link.href or ""
            norm_link_href = link_href.rstrip("/") if link_href != "/" else "/"

            # Check page instance matching
            if link.page_id and current_page:
                try:
                    if current_page.id == link.page_id:
                        link_is_active = True
                    elif current_page.is_descendant_of(link.page) and link.page.url != "/":
                        link_is_active = True
                except Exception:
                    pass

            # Check URL matching
            if not link_is_active and norm_link_href:
                if norm_link_href == "/":
                    if norm_current_path == "/":
                        link_is_active = True
                elif norm_current_path == norm_link_href:
                    link_is_active = True
                elif norm_current_path.startswith(norm_link_href + "/"):
                    link_is_active = True

            link.is_active = link_is_active
            if link_is_active:
                section_has_active = True

        section.has_active_link = section_has_active
        section.is_open = section_has_active or section.is_expanded
        result.append(section)

    return result




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
