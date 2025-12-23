from django.db import models
from wagtail.models import Page, Orderable
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, InlinePanel
from modelcluster.fields import ParentalKey

class HomePage(Page):
    body = RichTextField(blank=True)
    cta_text = models.CharField("Текст кнопки заклику", max_length=100, default="Приєднатися до нас")
    cta_link = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Посилання кнопки заклику"
    )

    content_panels = Page.content_panels + [
        FieldPanel('body'),
        InlinePanel('hero_images', label="Слайдер на головній"),
        InlinePanel('quick_links', label="Швидкі посилання"),
        FieldPanel('cta_text'),
        FieldPanel('cta_link'),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        # Get the latest 3 news pages
        from news.models import NewsPage
        context['latest_news'] = NewsPage.objects.live().public().order_by('-date')[:3]
        return context

class HeroImage(Orderable):
    page = ParentalKey(HomePage, on_delete=models.CASCADE, related_name='hero_images')
    image = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.CASCADE, related_name='+'
    )
    caption = models.CharField(blank=True, max_length=250, verbose_name="Підпис")

    panels = [
        FieldPanel('image'),
        FieldPanel('caption'),
    ]

class AboutPage(Page):
    subtitle = models.CharField("Підзаголовок", max_length=500, blank=True)
    body = RichTextField("Вміст", blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('subtitle'),
        FieldPanel('body'),
    ]

    parent_page_types = ['home.HomePage']
    subpage_types = ['home.StandardPage', 'home.DocumentPage']

class QuickLink(Orderable):
    page = ParentalKey(HomePage, on_delete=models.CASCADE, related_name='quick_links')
    title = models.CharField("Назва", max_length=100)
    link = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Посилання"
    )
    icon = models.CharField("Іконка (Bootstrap Icons class)", max_length=100, blank=True, 
                           help_text="Наприклад: bi-calendar-event, bi-file-earmark-person")

    panels = [
        FieldPanel('title'),
        FieldPanel('link'),
        FieldPanel('icon'),
    ]

class StandardPage(Page):
    """Generic page for static content like History, Rules, etc."""
    body = RichTextField("Вміст", blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('body'),
    ]

    parent_page_types = ['home.HomePage', 'home.AboutPage', 'home.EducationPage']
    subpage_types = []

    class Meta:
        verbose_name = "Стандартна сторінка"
        verbose_name_plural = "Стандартні сторінки"

class DocumentPage(Page):
    """Page for listing downloadable documents (for transparency/public information)"""
    intro = RichTextField("Вступний текст", blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        InlinePanel('documents', label="Документи"),
    ]

    parent_page_types = ['home.HomePage', 'home.AboutPage']
    subpage_types = []

    class Meta:
        verbose_name = "Сторінка документів"
        verbose_name_plural = "Сторінки документів"

class PageDocument(Orderable):
    page = ParentalKey(DocumentPage, on_delete=models.CASCADE, related_name='documents')
    document = models.ForeignKey(
        'wagtaildocs.Document',
        on_delete=models.CASCADE,
        related_name='+',
        verbose_name="Документ"
    )
    title = models.CharField("Назва", max_length=255)
    description = models.TextField("Опис", blank=True)

    panels = [
        FieldPanel('title'),
        FieldPanel('description'),
        FieldPanel('document'),
    ]

class EducationPage(Page):
    """Parent page for education-related subpages"""
    intro = RichTextField("Вступний текст", blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]

    parent_page_types = ['home.HomePage']
    subpage_types = ['home.StandardPage']

    class Meta:
        verbose_name = "Сторінка навчання"
        verbose_name_plural = "Сторінки навчання"
