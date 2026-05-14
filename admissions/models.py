from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from wagtail.admin.panels import (
    FieldPanel,
    FieldRowPanel,
    InlinePanel,
    MultiFieldPanel,
)
from wagtail.fields import RichTextField


class FormField(AbstractFormField):
    page = ParentalKey(
        "ApplicationFormPage",
        on_delete=models.CASCADE,
        related_name="form_fields",
    )


class ApplicationFormPage(AbstractEmailForm):

    def get_template(self, request, *args, **kwargs):
        # 1. Show the form ONLY if the user clicked the button (?form=1) 
        # OR if they are actively submitting the form (POST request)
        if request.GET.get('form') or request.method == 'POST':
            return 'admissions/application_form_page.html'
            
        # 2. Otherwise, show the introduction page by default
        return 'admissions/application_form_page_landing.html'

    def get_landing_page_template(self, request, *args, **kwargs):
        # 3. Wagtail calls the "Thank You" page the "landing page". 
        # We need to point this to a separate success template so it doesn't loop back to the intro.
        return 'admissions/application_form_page_success.html'

    page_description = "Форма вступу (створюється один раз)"

    intro = RichTextField(blank=True)
    rules_text = RichTextField(
        "Правила вступу",
        blank=True,
        help_text="Текст з правилами вступу, необхідними документами, датами тощо",
    )
    thank_you_text = RichTextField(blank=True)

    content_panels = AbstractEmailForm.content_panels + [
        FieldPanel("intro"),
        FieldPanel("rules_text"),
        InlinePanel("form_fields", label="Form fields"),
        FieldPanel("thank_you_text"),
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("from_address", classname="col6"),
                        FieldPanel("to_address", classname="col6"),
                    ]
                ),
                FieldPanel("subject"),
            ],
            "Email Settings",
        ),
    ]

    max_count = 1
    parent_page_types = ["home.HomePage"]

    class Meta:
        verbose_name = "Вступ (системна)"
        verbose_name_plural = "Вступ (системна)"
