from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page


class ApplicationFormPage(Page):
    """
    Admissions page that embeds a Google Form.

    The page has two views:
    - Landing page (default) — intro, rules, steps, CTA
    - Form page (?form=1) — embedded Google Form iframe
    """

    page_description = "Форма вступу"

    # ── Google Form integration ──────────────────────
    google_form_url = models.URLField(
        "Посилання Google Form (embed)",
        max_length=500,
        blank=True,
        help_text=(
            "Вставте посилання для вбудовування з Google Forms. "
            "Відкрийте форму → Надіслати → < > → скопіюйте src з iframe. "
            'Приклад: https://docs.google.com/forms/d/e/…/viewform?embedded=true'
        ),
    )

    # ── Page content ─────────────────────────────────
    intro = RichTextField(blank=True)
    rules_text = RichTextField(
        "Правила вступу",
        blank=True,
        help_text="Текст з правилами вступу, необхідними документами, датами тощо",
    )

    # ── Admin panels ─────────────────────────────────
    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [FieldPanel("google_form_url")],
            heading="Google Form",
        ),
        FieldPanel("intro"),
        FieldPanel("rules_text"),
    ]

    parent_page_types = ["home.HomePage", "home.ContentPage"]

    # ── Template routing ─────────────────────────────

    def get_template(self, request, *args, **kwargs):
        if request.GET.get("form"):
            return "admissions/application_form_page.html"
        return "admissions/application_form_page_landing.html"

    class Meta:
        verbose_name = "Вступ"
        verbose_name_plural = "Вступ"

    def __str__(self) -> str:
        return self.title
