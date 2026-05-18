from django.urls import reverse
from wagtail import hooks
from wagtail.admin.menu import MenuItem

from .models import StaffIndexPage


def _staff_admin_url() -> str:
    page = StaffIndexPage.objects.order_by("path").first()
    if page:
        return reverse("wagtailadmin_explore", args=[page.id])
    return reverse("wagtailadmin_explore_root")


@hooks.register("register_admin_menu_item")
def register_staff_menu_item() -> MenuItem:
    return MenuItem("Колектив", _staff_admin_url(), icon_name="group", order=250)
