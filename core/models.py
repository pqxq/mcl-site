from django.db import models
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.models import Orderable
from wagtail.snippets.models import register_snippet
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting


@register_snippet
class SidebarSection(ClusterableModel):
    """A collapsible section in the sidebar with custom page links"""
    title = models.CharField("Назва розділу", max_length=100)
    icon = models.CharField(
        "Іконка (Bootstrap Icons)", 
        max_length=50, 
        default="bi-folder",
        help_text="Наприклад: bi-book, bi-file-text, bi-calendar"
    )
    order = models.PositiveIntegerField("Порядок", default=0)
    is_expanded = models.BooleanField("Розгорнуто за замовчуванням", default=False)

    panels = [
        FieldPanel('title'),
        FieldPanel('icon'),
        FieldPanel('order'),
        FieldPanel('is_expanded'),
        InlinePanel('links', label="Посилання"),
    ]

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = "Розділ бічної панелі"
        verbose_name_plural = "Розділи бічної панелі"
        ordering = ['order', 'title']


class SidebarLink(Orderable):
    """A link within a sidebar section"""
    section = ParentalKey(SidebarSection, on_delete=models.CASCADE, related_name='links')
    label = models.CharField("Текст посилання", max_length=100)
    page = models.ForeignKey(
        'wagtailcore.Page', 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL, 
        related_name='+',
        verbose_name="Сторінка"
    )
    external_url = models.URLField("Зовнішнє посилання", blank=True)
    new_tab = models.BooleanField("Відкрити у новій вкладці", default=False)

    panels = [
        FieldPanel('label'),
        FieldPanel('page'),
        FieldPanel('external_url'),
        FieldPanel('new_tab'),
    ]

    @property
    def href(self) -> str:
        if self.page:
            return self.page.url
        return self.external_url

    def __str__(self) -> str:
        return self.label

    class Meta:
        verbose_name = "Посилання"
        verbose_name_plural = "Посилання"


@register_setting
class SEOSettings(BaseSiteSetting):
    meta_description_default = models.CharField("Опис за замовчуванням", max_length=255, blank=True)
    opengraph_image = models.ForeignKey(
        'wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL, related_name='+'
    )

    panels = [
        FieldPanel('meta_description_default'),
        FieldPanel('opengraph_image'),
    ]

    def __str__(self) -> str:
        return self.site.hostname


@register_setting
class SiteSettings(BaseSiteSetting):
    site_name = models.CharField("Назва сайту", max_length=120)
    default_og_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Зображення Open Graph за замовчуванням",
    )
    meta_description = models.CharField("Meta description", max_length=255, blank=True)
    google_analytics_id = models.CharField("Google Analytics ID", max_length=64, blank=True)

    panels = [
        FieldPanel("site_name"),
        FieldPanel("meta_description"),
        FieldPanel("default_og_image"),
        FieldPanel("google_analytics_id"),
    ]

    class Meta:
        verbose_name = "Налаштування сайту"

    def __str__(self) -> str:
        return self.site_name or self.site.hostname


class CTABlock(blocks.StructBlock):
    text = blocks.CharBlock(label="Текст", max_length=100)
    page = blocks.PageChooserBlock(required=False, label="Сторінка")
    url = blocks.URLBlock(required=False, label="Зовнішній URL")

    class Meta:
        icon = 'placeholder'
        label = 'Кнопка заклику'


class AnnouncementBlock(blocks.StructBlock):
    title = blocks.CharBlock(label="Заголовок")
    body = blocks.RichTextBlock(label="Опис")

    class Meta:
        icon = 'warning'
        label = 'Оголошення'


class CardBlock(blocks.StructBlock):
    title = blocks.CharBlock(label="Назва")
    body = blocks.TextBlock(label="Опис", required=False)
    image = ImageChooserBlock(label="Зображення", required=False)
    page = blocks.PageChooserBlock(required=False, label="Сторінка")
    url = blocks.URLBlock(required=False, label="Зовнішній URL")

    class Meta:
        icon = 'doc-full'
        label = 'Картка'


class CardListBlock(blocks.ListBlock):
    def __init__(self, **kwargs):
        super().__init__(CardBlock(), **kwargs)

    class Meta:
        icon = 'list-ul'
        label = 'Список карток'


class GalleryBlock(blocks.ListBlock):
    def __init__(self, **kwargs):
        super().__init__(ImageChooserBlock(), **kwargs)

    class Meta:
        icon = 'image'
        label = 'Галерея'
