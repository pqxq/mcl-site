from django.urls import reverse
from wagtail import hooks
from wagtail.admin.menu import MenuItem

from .models import ApplicationFormPage


def _admissions_admin_url() -> str:
    page = ApplicationFormPage.objects.order_by("path").first()
    if page:
        return reverse("wagtailadmin_explore", args=[page.id])
    return reverse("wagtailadmin_explore_root")


@hooks.register("register_admin_menu_item")
def register_admissions_menu_item() -> MenuItem:
    return MenuItem("Вступ", _admissions_admin_url(), icon_name="form", order=260)
