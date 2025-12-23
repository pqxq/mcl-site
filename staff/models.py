from django.db import models
from wagtail.models import Page, Orderable
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, InlinePanel
from modelcluster.fields import ParentalKey

class StaffIndexPage(Page):
    intro = RichTextField("Вступ", blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]

    subpage_types = ['staff.PersonPage']
    parent_page_types = ['home.HomePage']

class PersonPage(Page):
    position = models.CharField("Посада", max_length=100)
    education = models.CharField("Освіта", max_length=255, blank=True)
    category = models.CharField("Кваліфікаційна категорія", max_length=100, blank=True)
    experience = models.CharField("Стаж роботи", max_length=50, blank=True)
    bio = RichTextField("Біографія та досягнення", blank=True)
    photo = models.ForeignKey(
        'wagtailimages.Image',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',
        verbose_name="Фото"
    )

    content_panels = Page.content_panels + [
        FieldPanel('photo'),
        FieldPanel('position'),
        InlinePanel('subjects', label="Предмети"),
        FieldPanel('education'),
        FieldPanel('category'),
        FieldPanel('experience'),
        FieldPanel('bio'),
    ]

    parent_page_types = ['staff.StaffIndexPage']
    subpage_types = []

class TeacherSubject(Orderable):
    page = ParentalKey(PersonPage, on_delete=models.CASCADE, related_name='subjects')
    name = models.CharField("Назва предмета", max_length=100)

    panels = [
        FieldPanel('name'),
    ]
