from django.db import models
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.models import Orderable
from wagtail.snippets.models import register_snippet
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting


from django.db.models.signals import post_delete
from django.dispatch import receiver
from wagtail.models import Page



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

    @property
    def valid_links(self):
        """Returns only valid, live links for this section"""
        return [link for link in self.links.all() if link.is_valid]

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
    def is_valid(self) -> bool:
        """Check if link points to an active live page or valid external URL"""
        if self.page_id:
            try:
                page = self.page
                if page is None or not page.live:
                    return False
                return True
            except Exception:
                return False
        return bool(self.external_url and self.external_url.strip())

    @property
    def href(self) -> str:
        if self.page_id:
            try:
                page = self.page
                if page and page.live:
                    return page.url or ""
            except Exception:
                pass
        return self.external_url or ""

    @property
    def display_label(self) -> str:
        if self.page_id:
            try:
                page = self.page
                if page:
                    return page.title
            except Exception:
                pass
        return self.label

    def __str__(self) -> str:
        return self.display_label

    class Meta:
        verbose_name = "Посилання"
        verbose_name_plural = "Посилання"


@receiver(post_delete, sender=Page)
def cleanup_orphaned_sidebar_links_on_post_delete(sender, instance, **kwargs):
    SidebarLink.objects.filter(models.Q(page__isnull=True) | models.Q(page_id=instance.pk), external_url="").delete()




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
