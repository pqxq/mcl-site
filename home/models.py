from django.db import models
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from wagtail.models import Page, Orderable
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
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
    announcement = RichTextField(
        "Оголошення",
        blank=True,
        help_text="Текст оголошення, що відображається на головній сторінці під шапкою. Залиште порожнім, щоб приховати."
    )

    content_panels = Page.content_panels + [
        FieldPanel('announcement'),
        InlinePanel('quick_links', label="Швидкі посилання"),
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

    def save(self, *args, **kwargs):
        # Clear page cache so announcement changes are visible immediately
        from django.core.cache import cache
        cache.clear()
        return super().save(*args, **kwargs)

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

    # Hero & General section custom headers
    hero_badge = models.CharField(
        "Бейдж у шапці",
        max_length=100,
        blank=True,
        default="Миколаївський ліцей №9",
        help_text="Текст бейджа над заголовком у шапці"
    )
    mission_title = models.CharField(
        "Заголовок блоку місії",
        max_length=150,
        blank=True,
        default="Наша місія",
        help_text="Заголовок картки місії"
    )
    values_title = models.CharField(
        "Заголовок блоку цінностей",
        max_length=150,
        blank=True,
        default="Цінності ліцею",
        help_text="Заголовок картки цінностей"
    )
    profiles_title = models.CharField(
        "Заголовок блоку профілів",
        max_length=150,
        blank=True,
        default="Освітні напрями та пріоритети"
    )
    profiles_subtitle = models.CharField(
        "Підзаголовок блоку профілів",
        max_length=255,
        blank=True,
        default="Обирайте напрям, який відповідає талантам і прагненням майбутнього ліцеїста"
    )
    subpages_title = models.CharField(
        "Заголовок блоку підрозділів",
        max_length=150,
        blank=True,
        default="Розділи про наш ліцей"
    )
    subpages_subtitle = models.CharField(
        "Підзаголовок блоку підрозділів",
        max_length=255,
        blank=True,
        default="Ознайомтеся з історією, адміністрацією, педагогічним колективом та службами ліцею"
    )
    facilities_title = models.CharField(
        "Заголовок блоку інфраструктури",
        max_length=150,
        blank=True,
        default="Сучасний освітній простір"
    )
    facilities_subtitle = models.CharField(
        "Підзаголовок блоку інфраструктури",
        max_length=255,
        blank=True,
        default="Створюємо комфортні, безпечні та високотехнологічні умови для кожного ліцеїста"
    )
    faq_title = models.CharField(
        "Заголовок блоку FAQ",
        max_length=150,
        blank=True,
        default="Часті запитання батьків та учнів"
    )
    faq_subtitle = models.CharField(
        "Підзаголовок блоку FAQ",
        max_length=255,
        blank=True,
        default="Основна інформація про організацію освітнього процесу та вступ до ліцею"
    )

    # CTA Banner fields
    cta_title = models.CharField(
        "Заголовок заклику (CTA)",
        max_length=255,
        blank=True,
        default="Готові приєднатися до нашої ліцейної родини?",
        help_text="Головний заголовок блоку заклику до дії внизу сторінки"
    )
    cta_text = models.TextField(
        "Текст заклику (CTA)",
        blank=True,
        default="Миколаївський ліцей №9 відкриває двері для допитливих, талановитих та вмотивованих учнів. Оберіть якісну освіту та впевнений старт у майбутнє!",
        help_text="Опис під заголовком заклику"
    )
    cta_primary_text = models.CharField(
        "Текст основної кнопки",
        max_length=100,
        blank=True,
        default="Подати заяву на вступ"
    )
    cta_primary_link = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Посилання основної кнопки"
    )
    cta_secondary_text = models.CharField(
        "Текст другорядної кнопки",
        max_length=100,
        blank=True,
        default="Контакти та адреса"
    )
    cta_secondary_link = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Посилання другорядної кнопки"
    )

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('hero_badge'),
            FieldPanel('subtitle'),
            FieldPanel('intro'),
            InlinePanel('highlights', label="Ключові тези / пігулки"),
        ], heading="Головний огляд та вступ"),
        InlinePanel('stats', label="Статистичні показники"),
        MultiFieldPanel([
            FieldPanel('mission_title'),
            FieldPanel('mission'),
            FieldPanel('values_title'),
            FieldPanel('values'),
        ], heading="Місія та цінності (текст)"),
        InlinePanel('value_pillars', label="Картки цінностей"),
        MultiFieldPanel([
            FieldPanel('profiles_title'),
            FieldPanel('profiles_subtitle'),
        ], heading="Заголовки освітніх профілів"),
        InlinePanel('academic_profiles', label="Освітні профілі та напрями"),
        MultiFieldPanel([
            FieldPanel('subpages_title'),
            FieldPanel('subpages_subtitle'),
        ], heading="Заголовки навігації підрозділами"),
        MultiFieldPanel([
            FieldPanel('facilities_title'),
            FieldPanel('facilities_subtitle'),
            FieldPanel('building_image'),
        ], heading="Фото та інфраструктура"),
        InlinePanel('facilities', label="Елементи освітнього простору (укриття, лабораторії тощо)"),
        MultiFieldPanel([
            FieldPanel('history'),
            FieldPanel('achievements'),
        ], heading="Історія та досягнення"),
        MultiFieldPanel([
            FieldPanel('faq_title'),
            FieldPanel('faq_subtitle'),
        ], heading="Заголовки блоку FAQ"),
        InlinePanel('faqs', label="Часті запитання (FAQ)"),
        MultiFieldPanel([
            FieldPanel('cta_title'),
            FieldPanel('cta_text'),
            FieldPanel('cta_primary_text'),
            FieldPanel('cta_primary_link'),
            FieldPanel('cta_secondary_text'),
            FieldPanel('cta_secondary_link'),
        ], heading="Заклик до дії (CTA банер)"),
        MultiFieldPanel([
            FieldPanel('founded_year'),
            FieldPanel('students_count'),
            FieldPanel('teachers_count'),
        ], heading="Базові показники (застарілі)", classname="collapsed"),
    ]

    parent_page_types = ['home.HomePage']
    subpage_types = ['home.ContentPage', 'staff.StaffIndexPage']

    class Meta:
        verbose_name = "Про нас"

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        
        # 1. Child subpages under AboutPage
        child_pages = list(self.get_children().live().specific())
        
        # Map known page slugs to specific icons and badges
        subpages_data = []
        icon_mapping = {
            'istoriia-litseiu': ('bi-hourglass-split', 'Історія та спадщина', 'Шлях становлення, досягнення та традиції нашого навчального закладу від заснування до сьогодення.'),
            'kerivnytstvo-litseiu': ('bi-award-fill', 'Адміністрація', 'Керівний склад ліцею, що спрямовує освітній процес та втілює стратегію розвитку закладу.'),
            'pedahohichnyi-kolektyv': ('bi-people-fill', 'Педагогічний склад', 'Команда висококваліфікованих вчителів-новаторів, науковців та наставників.'),
            'sotsialno-psykholohichna-sluzhba': ('bi-heart-pulse-fill', 'Підтримка та турбота', 'Професійний психологічний супровід, профорієнтація та створення безпечного освітнього простору.'),
        }
        for child in child_pages:
            default_icon, default_tag, default_desc = icon_mapping.get(
                child.slug,
                ('bi-file-earmark-text-fill', 'Розділ ліцею', 'Докладна інформація про діяльність та структуру нашого освітнього закладу.')
            )
            subtitle = getattr(child, 'subtitle', '') or getattr(child, 'search_description', '')
            if not subtitle and hasattr(child, 'intro') and child.intro:
                from django.utils.html import strip_tags
                subtitle = strip_tags(str(child.intro))[:140]
            if not subtitle and hasattr(child, 'body') and child.body:
                from django.utils.html import strip_tags
                subtitle = strip_tags(str(child.body))[:140]
            
            subpages_data.append({
                'page': child,
                'title': child.title,
                'url': child.url,
                'slug': child.slug,
                'icon': default_icon,
                'tag': default_tag,
                'description': subtitle or default_desc,
            })
        context['about_subpages'] = subpages_data

        # 2. Admissions page link
        try:
            from admissions.models import ApplicationFormPage
            context['admissions_page'] = ApplicationFormPage.objects.live().first()
        except Exception:
            context['admissions_page'] = None

        # 3. Staff count / index page
        try:
            from staff.models import StaffIndexPage, PersonPage
            context['staff_index_page'] = StaffIndexPage.objects.live().first()
            context['live_staff_count'] = PersonPage.objects.live().count()
        except Exception:
            context['staff_index_page'] = None
            context['live_staff_count'] = 0

        # 4. Gallery page link & preview images
        try:
            from gallery.models import GalleryIndexPage, GalleryImage
            context['gallery_index_page'] = GalleryIndexPage.objects.live().first()
            context['campus_gallery_images'] = GalleryImage.objects.select_related('image', 'page').order_by('-id')[:4]
        except Exception:
            context['gallery_index_page'] = None
            context['campus_gallery_images'] = []

        return context

    def __str__(self) -> str:
        return self.title


class AboutPageStat(Orderable):
    page = ParentalKey(AboutPage, on_delete=models.CASCADE, related_name='stats')
    number = models.CharField("Показник / Число", max_length=50, help_text="Наприклад: 1991, 500+, 100%, 45")
    title = models.CharField("Назва показника", max_length=100, help_text="Наприклад: Рік заснування, Учнів ліцею, Вчителів")
    description = models.CharField("Короткий підпис", max_length=200, blank=True, help_text="Наприклад: Понад 30 років академічних традицій")
    icon = models.CharField("Іконка (Bootstrap Icons)", max_length=50, default="bi-calendar-check", help_text="Наприклад: bi-calendar-check, bi-people-fill, bi-person-badge-fill, bi-trophy-fill")

    panels = [
        FieldPanel('number'),
        FieldPanel('title'),
        FieldPanel('description'),
        FieldPanel('icon'),
    ]

    def __str__(self) -> str:
        return f"{self.title}: {self.number}"


class AboutPageValuePillar(Orderable):
    page = ParentalKey(AboutPage, on_delete=models.CASCADE, related_name='value_pillars')
    title = models.CharField("Назва цінності", max_length=150, help_text="Наприклад: Академічна якість та доброчесність")
    description = models.TextField("Опис цінності", help_text="Коротке пояснення суті цієї цінності для учнів та педагогів")
    icon = models.CharField("Іконка (Bootstrap Icons)", max_length=50, default="bi-mortarboard-fill", help_text="Наприклад: bi-mortarboard-fill, bi-people-fill, bi-lightbulb-fill, bi-shield-fill-check")

    panels = [
        FieldPanel('title'),
        FieldPanel('description'),
        FieldPanel('icon'),
    ]

    def __str__(self) -> str:
        return self.title


class AboutPageProfile(Orderable):
    page = ParentalKey(AboutPage, on_delete=models.CASCADE, related_name='academic_profiles')
    badge = models.CharField("Категорія / Бейдж", max_length=100, default="Профіль", help_text="Наприклад: Точні науки, Мови та світ, Дослідження, Суспільство")
    title = models.CharField("Назва профілю / напряму", max_length=150, help_text="Наприклад: Математика & IT, Філологічний напрям")
    description = models.TextField("Опис напряму", help_text="Що вивчають учні на цьому напрямі та які навички здобувають")
    tags = models.CharField("Теги предметів (через кому)", max_length=255, blank=True, help_text="Наприклад: Математика, Інформатика, Алгоритми")
    icon = models.CharField("Іконка (Bootstrap Icons)", max_length=50, default="bi-cpu-fill", help_text="Наприклад: bi-cpu-fill, bi-translate, bi-flask-fill, bi-bank")

    panels = [
        FieldPanel('badge'),
        FieldPanel('title'),
        FieldPanel('description'),
        FieldPanel('tags'),
        FieldPanel('icon'),
    ]

    def get_tag_list(self):
        if not self.tags:
            return []
        return [t.strip() for t in self.tags.split(',') if t.strip()]

    def __str__(self) -> str:
        return self.title


class AboutPageFacility(Orderable):
    page = ParentalKey(AboutPage, on_delete=models.CASCADE, related_name='facilities')
    title = models.CharField("Назва елемента простору", max_length=150, help_text="Наприклад: Сертифіковане укриття, Мультимедійні класи")
    description = models.TextField("Опис оснащення та можливостей", help_text="Короткий опис облаштування та переваг для учнів")
    icon = models.CharField("Іконка (Bootstrap Icons)", max_length=50, default="bi-shield-check", help_text="Наприклад: bi-shield-check, bi-display, bi-trophy, bi-journal-bookmark")

    panels = [
        FieldPanel('title'),
        FieldPanel('description'),
        FieldPanel('icon'),
    ]

    def __str__(self) -> str:
        return self.title


class AboutPageFAQ(Orderable):
    page = ParentalKey(AboutPage, on_delete=models.CASCADE, related_name='faqs')
    question = models.CharField("Запитання", max_length=300, help_text="Наприклад: Як вступити до Миколаївського ліцею №9?")
    answer = RichTextField("Відповідь", help_text="Розгорнута відповідь з можливістю додавати посилання та форматування")

    panels = [
        FieldPanel('question'),
        FieldPanel('answer'),
    ]

    def __str__(self) -> str:
        return self.question


class AboutPageHighlight(Orderable):
    page = ParentalKey(AboutPage, on_delete=models.CASCADE, related_name='highlights')
    title = models.CharField("Текст тези/переваги", max_length=150, help_text="Наприклад: Поглиблене вивчення предметів")
    icon = models.CharField("Іконка (Bootstrap Icons)", max_length=50, default="bi-check-circle-fill", help_text="Наприклад: bi-check-circle-fill, bi-shield-lock-fill, bi-laptop, bi-stars")

    panels = [
        FieldPanel('title'),
        FieldPanel('icon'),
    ]

    def __str__(self) -> str:
        return self.title




