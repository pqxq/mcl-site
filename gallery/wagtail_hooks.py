from django.urls import reverse
from wagtail import hooks
from wagtail.admin.menu import MenuItem

from .models import GalleryIndexPage


def _gallery_admin_url() -> str:
    page = GalleryIndexPage.objects.order_by("path").first()
    if page:
        return reverse("wagtailadmin_explore", args=[page.id])
    return reverse("wagtailadmin_explore_root")


@hooks.register("register_admin_menu_item")
def register_gallery_menu_item() -> MenuItem:
    return MenuItem("Галерея", _gallery_admin_url(), icon_name="image", order=240)
