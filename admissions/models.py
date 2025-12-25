from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import (
    FieldPanel, FieldRowPanel,
    InlinePanel, MultiFieldPanel
)
from wagtail.fields import RichTextField
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField

class FormField(AbstractFormField):
    page = ParentalKey('ApplicationFormPage', on_delete=models.CASCADE, related_name='form_fields')

class ApplicationFormPage(AbstractEmailForm):
    
    page_description = "Форма вступу (створюється один раз)"
    
    intro = RichTextField(blank=True)
    rules_text = RichTextField("Правила вступу", blank=True, 
                              help_text="Текст з правилами вступу, необхідними документами, датами тощо")
    thank_you_text = RichTextField(blank=True)

    content_panels = AbstractEmailForm.content_panels + [
        FieldPanel('intro'),
        FieldPanel('rules_text'),
        InlinePanel('form_fields', label="Form fields"),
        FieldPanel('thank_you_text'),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('from_address', classname="col6"),
                FieldPanel('to_address', classname="col6"),
            ]),
            FieldPanel('subject'),
        ], "Email Settings"),
    ]

    max_count = 1
    parent_page_types = ['home.HomePage']
    
    class Meta:
        verbose_name = "Вступ (системна)"
