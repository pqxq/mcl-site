"""
Management command to create the full site page tree structure.

Creates all section pages and sub-pages using the correct Wagtail page types.
Skips pages that already exist (matched by slug under the same parent).

Usage:
    python manage.py create_site_structure
"""

from django.core.management.base import BaseCommand
from wagtail.models import Page

from home.models import HomePage, AboutPage, ContentPage
from news.models import NewsIndexPage
from gallery.models import GalleryIndexPage
from staff.models import StaffIndexPage
from admissions.models import ApplicationFormPage


class Command(BaseCommand):
    help = "Create the full site page tree structure for MCL Lyceum"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.created = 0
        self.skipped = 0

    def add_child_page(self, parent, page_cls, title, slug, **extra_fields):
        """
        Add a child page under `parent` if it doesn't already exist.
        Returns the (possibly pre-existing) child page.
        """
        existing = page_cls.objects.child_of(parent).filter(slug=slug).first()
        if existing:
            self.stdout.write(f"  ⏩ Існує: {title} ({slug})")
            self.skipped += 1
            return existing

        page = page_cls(title=title, slug=slug, **extra_fields)
        parent.add_child(instance=page)
        page.save_revision().publish()
        self.stdout.write(self.style.SUCCESS(f"  ✅ Створено: {title} ({slug})"))
        self.created += 1
        return page

    def add_content_page(self, parent, title, slug):
        """Shortcut for adding a ContentPage."""
        return self.add_child_page(parent, ContentPage, title, slug)

    def handle(self, *args, **options):
        # Find the HomePage
        home = HomePage.objects.live().first()
        if not home:
            self.stderr.write(self.style.ERROR(
                "❌ HomePage не знайдено! Створіть її через Wagtail Admin."
            ))
            return

        self.stdout.write(f"\n📍 Головна: {home.title} (id={home.pk})\n")

        # ─── Про ліцей ───────────────────────────────────────────
        self.stdout.write(self.style.MIGRATE_HEADING("\n── Про ліцей ──"))
        about = self.add_child_page(home, AboutPage, "Про ліцей", "pro-litsei")

        self.add_content_page(about, "Історія ліцею", "istoriia-litseiu")
        self.add_content_page(about, "Керівництво ліцею", "kerivnytstvo-litseiu")
        self.add_child_page(about, StaffIndexPage, "Педагогічний колектив", "pedahohichnyi-kolektyv")
        self.add_content_page(about, "Соціально-психологічна служба", "sotsialno-psykholohichna-sluzhba")

        # ─── Публічна інформація ──────────────────────────────────
        self.stdout.write(self.style.MIGRATE_HEADING("\n── Публічна інформація ──"))
        public_info = self.add_content_page(home, "Публічна інформація", "publichna-informatsiia")

        self.add_content_page(public_info, "Установчі документи", "ustanovchi-dokumenty")
        self.add_content_page(public_info, "Нормативні документи", "normatyvni-dokumenty")
        self.add_content_page(public_info, "Фінансова діяльність", "finansova-diialnist")
        self.add_content_page(public_info, "Положення", "polozhennia")
        self.add_content_page(public_info, "Якість освіти", "yakist-osvity")
        self.add_content_page(public_info, "Безпека життєдіяльності", "bezpeka-zhyttiediialnisti")
        self.add_content_page(public_info, "Профілактика булінгу та жорстокого поводження", "profilaktyka-bulinhu")
        self.add_child_page(
            public_info, ApplicationFormPage,
            "Вступ до ліцею", "vstup-do-litseiu",
        )
        self.add_content_page(public_info, "Інклюзія", "inkliuziia")

        # ─── Освітній процес ──────────────────────────────────────
        self.stdout.write(self.style.MIGRATE_HEADING("\n── Освітній процес ──"))
        education = self.add_content_page(home, "Освітній процес", "osvitnii-protses")

        self.add_content_page(education, "Розклад", "rozklad")
        self.add_content_page(education, "Критерії оцінювання з предметів", "kryterii-otsiniuvannia")
        self.add_content_page(education, "Досягнення", "dosiahnennia")
        self.add_content_page(education, "Все про НМТ (ЗНО)", "vse-pro-nmt-zno")

        # ─── Виховна робота ───────────────────────────────────────
        self.stdout.write(self.style.MIGRATE_HEADING("\n── Виховна робота ──"))
        upbringing = self.add_content_page(home, "Виховна робота", "vykhovna-robota")

        self.add_content_page(upbringing, "Учнівське самоврядування", "uchnivske-samovriaduvannia")
        self.add_content_page(upbringing, "Патріотичне виховання", "patriotychne-vykhovannia")
        self.add_content_page(upbringing, "Безбар'єрність", "bezbar-iernist")

        # ─── Top-level standalone pages ───────────────────────────
        self.stdout.write(self.style.MIGRATE_HEADING("\n── Окремі розділи ──"))
        self.add_content_page(home, "Батькам", "batkam")
        self.add_content_page(home, "Педагогам", "pedahoham")

        # News (NewsIndexPage)
        self.add_child_page(home, NewsIndexPage, "Новини", "novyny")

        # Contacts
        self.add_content_page(home, "Контакти", "kontakty")

        # Gallery (GalleryIndexPage)
        self.add_child_page(home, GalleryIndexPage, "Галерея", "gallery")

        # ─── Summary ─────────────────────────────────────────────
        self.stdout.write(self.style.MIGRATE_HEADING("\n── Результат ──"))
        self.stdout.write(self.style.SUCCESS(
            f"✅ Створено: {self.created} сторінок"
        ))
        if self.skipped:
            self.stdout.write(f"⏩ Пропущено (вже існують): {self.skipped} сторінок")
        self.stdout.write("")
