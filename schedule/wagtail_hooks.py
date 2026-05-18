from django.urls import reverse
from wagtail import hooks
from wagtail.admin.menu import MenuItem


@hooks.register("register_admin_menu_item")
def register_schedule_menu_item() -> MenuItem:
    return MenuItem("Розклад", reverse("wagtailsnippets:index"), icon_name="date", order=270)
