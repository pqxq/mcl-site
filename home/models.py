from django.db import models
from wagtail.models import Page, Orderable
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, InlinePanel
from modelcluster.fields import ParentalKey

class HomePage(Page):
    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('body'),
        InlinePanel('hero_images', label="Слайдер на головній"),
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
    subpage_types = []
