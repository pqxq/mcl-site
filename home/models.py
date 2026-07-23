from django.db import models
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from wagtail.models import Page, Orderable
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, InlinePanel
from modelcluster.fields import ParentalKey


class HomePage(Page):
    """Main landing page of the site"""
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

    # HomePage can contain any page type
    subpage_types = [
        'home.AboutPage',
        'home.ContentPage',
        'news.NewsIndexPage',
        'admissions.ApplicationFormPage',
        'staff.StaffIndexPage',
        'documents.DocumentsIndexPage',
        'gallery.GalleryIndexPage',
    ]

    max_count = 1

    @method_decorator(cache_page(60 * 15))
    def serve(self, request, *args, **kwargs):
        return super().serve(request, *args, **kwargs)

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        from news.models import NewsPage
        context["latest_news"] = (
            NewsPage.objects.live()
            .public()
            .select_related("owner")
            .only(
                "title",
                "slug",
                "first_published_at",
                "search_description",
                "live",
                "owner",
                "date",
                "intro",
                "image",
            )
            .order_by("-first_published_at")[:3]
        )
        
        # Get images for the ticker from gallery albums
        from gallery.models import GalleryImage
        ticker_images = GalleryImage.objects.select_related('image', 'page').order_by('-page__first_published_at')[:30]
        # Provide album and image IDs for linking
        context['ticker_images'] = [
            {
                'image': img.image,
                'caption': img.caption,
                'album': img.page,
                'image_id': img.id,
            }
            for img in ticker_images
        ]
        
        return context

    class Meta:
        verbose_name = "Головна сторінка"

    def __str__(self) -> str:
        return self.title

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

    def __str__(self) -> str:
        return self.caption or self.image.title


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
    icon = models.CharField("Іконка (Bootstrap Icons)", max_length=100, blank=True,
                           help_text="Наприклад: bi-calendar-event, bi-file-earmark-person")

    panels = [
        FieldPanel('title'),
        FieldPanel('link'),
        FieldPanel('icon'),
    ]

    def __str__(self) -> str:
        return self.title


class ContentPage(Page):
    """
    Universal content page for any static content:
    - About pages
    - History, Rules, etc.
    - Education information
    - Any other informational pages
    """
    
    # Page type description shown in add subpage menu
    page_description = "Універсальна сторінка для будь-якого контенту"
    
    subtitle = models.CharField("Підзаголовок", max_length=500, blank=True)
    body = RichTextField("Вміст", blank=True)
    featured_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Зображення"
    )

    content_panels = Page.content_panels + [
        FieldPanel('subtitle'),
        FieldPanel('featured_image'),
        FieldPanel('body'),
    ]

    # ContentPage can be nested under HomePage, AboutPage, or other ContentPages
    parent_page_types = [
        'home.HomePage',
        'home.AboutPage',
        'home.ContentPage',
    ]
    subpage_types = [
        'home.ContentPage',
        'staff.StaffIndexPage',
        'documents.DocumentsIndexPage',
        'admissions.ApplicationFormPage',
    ]

    class Meta:
        verbose_name = "Сторінка контенту"
        verbose_name_plural = "Сторінки контенту"

    def __str__(self) -> str:
        return self.title


class AboutPage(Page):
    """Special About page with unique design and structured content"""

    page_description = "Сторінка про заклад"

    subtitle = models.CharField("Девіз/Слоган", max_length=500, blank=True,
                               help_text="Короткий слоган або девіз закладу")
    intro = RichTextField("Вступний текст", blank=True,
                         help_text="Коротке представлення закладу")
    mission = RichTextField("Місія", blank=True,
                           help_text="Місія та цілі закладу")
    history = RichTextField("Історія", blank=True,
                           help_text="Історія закладу")
    values = RichTextField("Цінності", blank=True,
                          help_text="Основні цінності та принципи")
    achievements = RichTextField("Досягнення", blank=True,
                                help_text="Ключові досягнення закладу")
    founded_year = models.PositiveIntegerField("Рік заснування", null=True, blank=True)
    students_count = models.PositiveIntegerField("Кількість учнів", null=True, blank=True)
    teachers_count = models.PositiveIntegerField("Кількість вчителів", null=True, blank=True)
    building_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Фото закладу",
        help_text="Фото будівлі або території закладу"
    )

    content_panels = Page.content_panels + [
        FieldPanel('subtitle'),
        FieldPanel('intro'),
        FieldPanel('mission'),
        FieldPanel('history'),
        FieldPanel('values'),
        FieldPanel('achievements'),
        FieldPanel('founded_year'),
        FieldPanel('students_count'),
        FieldPanel('teachers_count'),
        FieldPanel('building_image'),
    ]

    parent_page_types = ['home.HomePage']
    subpage_types = ['home.ContentPage', 'staff.StaffIndexPage']

    class Meta:
        verbose_name = "Про нас"

    def __str__(self) -> str:
        return self.title


