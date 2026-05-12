from django.db import models
from django.utils import timezone

from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page
from wagtail.search import index
from wagtail.snippets.models import register_snippet

from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from taggit.models import TaggedItemBase


def current_year() -> int:
    return timezone.now().year


class PublicDocumentPageTag(TaggedItemBase):
    content_object = ParentalKey(
        "PublicDocumentPage",
        related_name="tagged_items",
        on_delete=models.CASCADE,
    )


@register_snippet
class DocumentType(models.Model):
    """Admin-manageable document types"""
    name = models.CharField("Назва", max_length=100)
    slug = models.SlugField(
        "Ідентифікатор",
        max_length=100,
        unique=True,
        help_text="Унікальний ідентифікатор (латиницею, без пробілів)",
    )

    panels = [
        FieldPanel("name"),
        FieldPanel("slug"),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Тип документу"
        verbose_name_plural = "Типи документів"
        ordering = ["name"]


class DocumentsIndexPage(Page):
    """Index page for public documents with filtering"""

    page_description = "Розділ документів (створюється один раз)"

    intro = RichTextField("Вступний текст", blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    max_count = 1
    parent_page_types = ["home.HomePage"]
    subpage_types = ["documents.PublicDocumentPage"]

    class Meta:
        verbose_name = "Документи (системна)"
        verbose_name_plural = "Документи"

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        documents = (
            PublicDocumentPage.objects.child_of(self)
            .live()
            .public()
            .select_related("doc_type")
            .prefetch_related("tags")
            .order_by("-date", "-first_published_at")
        )

        doc_type = request.GET.get("type", "").strip()
        year = request.GET.get("year", "").strip()
        tag = request.GET.get("tag", "").strip()

        if doc_type:
            documents = documents.filter(doc_type__slug=doc_type)

        if year:
            try:
                documents = documents.filter(year=int(year))
            except ValueError:
                documents = documents.none()

        if tag:
            documents = documents.filter(tags__name=tag).distinct()

        available_years = list(
            PublicDocumentPage.objects.child_of(self)
            .live()
            .public()
            .order_by()
            .values_list("year", flat=True)
            .distinct()
        )
        available_years.sort(reverse=True)

        context["documents"] = documents
        context["current_type"] = doc_type
        context["current_year"] = year
        context["current_tag"] = tag
        context["doc_type_choices"] = DocumentType.objects.all()
        context["available_years"] = available_years
        return context


class PublicDocumentPage(Page):
    """Single public document with metadata and file attachment"""
    date = models.DateField("Дата", default=timezone.now)
    description = RichTextField("Опис", blank=True)
    doc_file = models.ForeignKey(
        "wagtaildocs.Document",
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Файл документа",
    )
    doc_type = models.ForeignKey(
        DocumentType,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Тип документу",
    )
    year = models.PositiveSmallIntegerField("Рік", default=current_year)

    tags = ClusterTaggableManager(through=PublicDocumentPageTag, blank=True, verbose_name="Теги")

    search_fields = Page.search_fields + [
        index.SearchField("title", boost=2),
        index.SearchField("description"),
    ]

    content_panels = Page.content_panels + [
        FieldPanel("date"),
        FieldPanel("doc_type"),
        FieldPanel("year"),
        FieldPanel("doc_file"),
        FieldPanel("description"),
        FieldPanel("tags"),
    ]

    parent_page_types = ["documents.DocumentsIndexPage"]
    subpage_types = []

    class Meta:
        verbose_name = "Публічний документ"
        verbose_name_plural = "Публічні документи"
