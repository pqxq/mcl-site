from django import forms
from django.core.mail import EmailMessage
from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import (
    FieldPanel,
    FieldRowPanel,
    InlinePanel,
    MultiFieldPanel,
)
from wagtail.contrib.forms.forms import FormBuilder
from wagtail.contrib.forms.models import (
    FORM_FIELD_CHOICES,
    AbstractEmailForm,
    AbstractFormField,
)
from wagtail.fields import RichTextField




class ApplicationFormBuilder(FormBuilder):
    def create_file_field(self, field, options):
        return forms.FileField(**options)

    def create_image_field(self, field, options):
        return forms.ImageField(**options)


class FormField(AbstractFormField):
    CHOICES = FORM_FIELD_CHOICES + (
        ("file", "Файл / Фото заяви"),
        ("image", "Зображення"),
    )
    field_type = models.CharField(
        verbose_name="Тип поля",
        max_length=16,
        choices=CHOICES,
    )

    page = ParentalKey(
        "ApplicationFormPage",
        on_delete=models.CASCADE,
        related_name="form_fields",
    )

    def __str__(self) -> str:
        return self.label


class ApplicationFormPage(AbstractEmailForm):
    form_builder = ApplicationFormBuilder


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

    def send_mail(self, form):
        addresses = [x.strip() for x in self.to_address.split(",") if x.strip()]
        if not addresses:
            return

        content = self.render_email(form)
        email = EmailMessage(
            subject=self.subject,
            body=content,
            from_email=self.from_address or None,
            to=addresses,
        )

        for field_name, uploaded_file in form.files.items():
            email.attach(
                uploaded_file.name,
                uploaded_file.read(),
                uploaded_file.content_type,
            )

        email.send()

    page_description = "Форма вступу"

    intro = RichTextField(blank=True)
    rules_text = RichTextField(
        "Правила вступу",
        blank=True,
        help_text="Текст з правилами вступу, необхідними документами, датами тощо",
    )
    sample_application_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Зразок заяви (зображення)",
        help_text="Зображення зразка заяви для перегляду у формі",
    )
    sample_application_document = models.ForeignKey(
        "wagtaildocs.Document",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Зразок заяви (скачуваний документ PDF/DOCX)",
        help_text="Документ-бланк зразка заяви для завантаження",
    )
    sample_application_description = RichTextField(
        "Інструкція до заяви / опис зразка",
        blank=True,
        help_text="Короткі вказівки, як заповнити та підписати заяву перед фотографуванням",
    )
    thank_you_text = RichTextField(blank=True)

    content_panels = AbstractEmailForm.content_panels + [
        FieldPanel("intro"),
        FieldPanel("rules_text"),
        MultiFieldPanel(
            [
                FieldPanel("sample_application_image"),
                FieldPanel("sample_application_document"),
                FieldPanel("sample_application_description"),
            ],
            heading="Зразок заяви на вступ",
        ),
        InlinePanel("form_fields", label="Поля форми"),
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

    parent_page_types = ["home.HomePage", "home.ContentPage"]

    class Meta:
        verbose_name = "Вступ"
        verbose_name_plural = "Вступ"

    def __str__(self) -> str:
        return self.title

