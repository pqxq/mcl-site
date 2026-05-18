from django.urls import reverse
from wagtail import hooks
from wagtail.admin.menu import MenuItem

from .models import NewsIndexPage


def _news_admin_url() -> str:
    page = NewsIndexPage.objects.order_by("path").first()
    if page:
        return reverse("wagtailadmin_explore", args=[page.id])
    return reverse("wagtailadmin_explore_root")


@hooks.register("register_admin_menu_item")
def register_news_menu_item() -> MenuItem:
    return MenuItem("Новини", _news_admin_url(), icon_name="doc-full-inverse", order=230)
