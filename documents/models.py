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


class PublicDocumentPageTag(TaggedItemBase):
    content_object = ParentalKey(
        'PublicDocumentPage',
        related_name='tagged_items',
        on_delete=models.CASCADE
    )


@register_snippet
class DocumentType(models.Model):
    """Admin-manageable document types"""
    name = models.CharField("Назва", max_length=100)
    slug = models.SlugField("Ідентифікатор", max_length=100, unique=True,
                           help_text="Унікальний ідентифікатор (латиницею, без пробілів)")

    panels = [
        FieldPanel('name'),
        FieldPanel('slug'),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Тип документу"
        verbose_name_plural = "Типи документів"
        ordering = ['name']


class DocumentsIndexPage(Page):
    """Index page for public documents with filtering"""
    
    page_description = "Розділ документів (створюється один раз)"
    
    intro = RichTextField("Вступний текст", blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]

    max_count = 1
    parent_page_types = ['home.HomePage']
    subpage_types = ['documents.PublicDocumentPage']

    class Meta:
        verbose_name = "Документи (системна)"
        verbose_name_plural = "Документи"

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        items = self.get_children().live().specific().order_by('-first_published_at')

        doc_type = request.GET.get('type') or ''
        year = request.GET.get('year') or ''
        tag = request.GET.get('tag') or ''

        # Apply filters on specific pages
        def matches_filters(page):
            ok = True
            if doc_type:
                page_type_slug = getattr(page.doc_type, 'slug', '') if page.doc_type else ''
                ok = ok and page_type_slug == doc_type
            if year:
                try:
                    ok = ok and int(getattr(page, 'year', 0)) == int(year)
                except ValueError:
                    ok = False
            if tag:
                ok = ok and (tag in [t.name for t in getattr(page, 'tags', []).all()])
            return ok

        items = [p for p in items if matches_filters(p)]

        context['documents'] = items
        context['current_type'] = doc_type
        context['current_year'] = year
        context['current_tag'] = tag
        context['doc_type_choices'] = DocumentType.objects.all()
        context['available_years'] = sorted({getattr(p, 'year', timezone.now().year) for p in self.get_children().live().specific()}, reverse=True)
        return context


class PublicDocumentPage(Page):
    """Single public document with metadata and file attachment"""
    date = models.DateField("Дата", default=timezone.now)
    description = RichTextField("Опис", blank=True)
    doc_file = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Файл документа"
    )
    doc_type = models.ForeignKey(
        DocumentType,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Тип документу"
    )
    year = models.PositiveSmallIntegerField("Рік", default=timezone.now().year)

    tags = ClusterTaggableManager(through=PublicDocumentPageTag, blank=True, verbose_name="Теги")

    search_fields = Page.search_fields + [
        index.SearchField('title', boost=2),
        index.SearchField('description'),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('date'),
        FieldPanel('doc_type'),
        FieldPanel('year'),
        FieldPanel('doc_file'),
        FieldPanel('description'),
        FieldPanel('tags'),
    ]

    parent_page_types = ['documents.DocumentsIndexPage']
    subpage_types = []

    class Meta:
        verbose_name = "Публічний документ"
        verbose_name_plural = "Публічні документи"
