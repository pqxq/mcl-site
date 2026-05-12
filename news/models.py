from django.db import models
from django.utils import timezone
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from taggit.models import Tag, TaggedItemBase
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page
from wagtail.search import index


class NewsPageTag(TaggedItemBase):
    content_object = ParentalKey(
        "NewsPage",
        related_name="tagged_items",
        on_delete=models.CASCADE,
    )


class NewsIndexPage(Page):
    """Index page listing all news articles"""

    page_description = "Розділ новин (створюється один раз)"

    intro = RichTextField("Вступний текст", blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    max_count = 1
    parent_page_types = ["home.HomePage"]
    subpage_types = ["news.NewsPage"]

    class Meta:
        verbose_name = "Новини (системна)"
        verbose_name_plural = "Новини"

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        all_news_items = (
            NewsPage.objects.child_of(self)
            .live()
            .public()
            .prefetch_related("tags")
            .order_by("-date", "-first_published_at")
        )

        tag_filter = request.GET.get("tag", "").strip()
        news_items = all_news_items
        if tag_filter:
            news_items = news_items.filter(tags__name=tag_filter).distinct()

        all_tags = sorted(
            Tag.objects.filter(newspage__in=all_news_items.values_list("id", flat=True))
            .values_list("name", flat=True)
            .distinct(),
            key=str.casefold,
        )

        context["news_items"] = news_items
        context["all_tags"] = all_tags
        context["current_tag"] = tag_filter
        return context


class NewsPage(Page):
    """Individual news article"""
    date = models.DateField("Дата публікації", default=timezone.now)
    intro = models.CharField("Короткий опис", max_length=250)
    body = RichTextField("Текст новини", blank=True)
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Головне зображення",
    )
    tags = ClusterTaggableManager(through=NewsPageTag, blank=True, verbose_name="Теги")

    search_fields = Page.search_fields + [
        index.SearchField("title", boost=2),
        index.SearchField("intro", boost=2),
        index.SearchField("body"),
    ]

    content_panels = Page.content_panels + [
        FieldPanel("date"),
        FieldPanel("intro"),
        FieldPanel("body"),
        FieldPanel("image"),
        FieldPanel("tags"),
    ]

    parent_page_types = ["news.NewsIndexPage"]
    subpage_types = []

    class Meta:
        verbose_name = "Новина"
        verbose_name_plural = "Новини"
