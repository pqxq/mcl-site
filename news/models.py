from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel
from wagtail.search import index
from django.utils import timezone


class NewsIndexPage(Page):
    """Index page listing all news articles"""
    intro = RichTextField("Вступний текст", blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]

    parent_page_types = ['home.HomePage']
    subpage_types = ['NewsPage']

    class Meta:
        verbose_name = "Сторінка новин"
        verbose_name_plural = "Сторінки новин"

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        # Get published news, ordered by date descending
        context['news_items'] = self.get_children().live().order_by('-first_published_at')
        return context


class NewsPage(Page):
    """Individual news article"""
    date = models.DateField("Дата публікації", default=timezone.now)
    intro = models.CharField("Короткий опис", max_length=250)
    body = RichTextField("Текст новини", blank=True)
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Головне зображення"
    )
    
    search_fields = Page.search_fields + [
        index.SearchField('intro'),
        index.SearchField('body'),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('date'),
        FieldPanel('intro'),
        FieldPanel('body'),
        FieldPanel('image'),
    ]

    parent_page_types = ['NewsIndexPage']
    subpage_types = []

    class Meta:
        verbose_name = "Новина"
        verbose_name_plural = "Новини"
