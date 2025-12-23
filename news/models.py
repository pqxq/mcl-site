from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel
from wagtail.search import index
from django.utils import timezone
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from taggit.models import TaggedItemBase


class NewsPageTag(TaggedItemBase):
    content_object = ParentalKey(
        'NewsPage',
        related_name='tagged_items',
        on_delete=models.CASCADE
    )


class NewsIndexPage(Page):
    """Index page listing all news articles"""
    intro = RichTextField("Вступний текст", blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]

    parent_page_types = ['home.HomePage']
    subpage_types = ['news.NewsPage']

    class Meta:
        verbose_name = "Сторінка новин"
        verbose_name_plural = "Сторінки новин"

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        # Get published news, ordered by date descending
        news_items = self.get_children().live().specific().order_by('-first_published_at')
        
        # Filter by tag if requested
        tag_filter = request.GET.get('tag', '')
        if tag_filter:
            news_items = [item for item in news_items if tag_filter in [tag.name for tag in item.tags.all()]]
        
        context['news_items'] = news_items
        
        # Get all tags for filtering
        from taggit.models import Tag
        from news.models import NewsPage
        news_pages = NewsPage.objects.filter(id__in=[p.id for p in self.get_children().live()])
        all_tags = Tag.objects.filter(newspage__in=news_pages).distinct()
        context['all_tags'] = all_tags
        context['current_tag'] = tag_filter
        
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
    tags = ClusterTaggableManager(through=NewsPageTag, blank=True, verbose_name="Теги")
    
    search_fields = Page.search_fields + [
        index.SearchField('intro'),
        index.SearchField('body'),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('date'),
        FieldPanel('intro'),
        FieldPanel('body'),
        FieldPanel('image'),
        FieldPanel('tags'),
    ]

    parent_page_types = ['news.NewsIndexPage']
    subpage_types = []

    class Meta:
        verbose_name = "Новина"
        verbose_name_plural = "Новини"
