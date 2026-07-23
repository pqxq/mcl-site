"""
Django management command to set up the complete site structure.
Creates all pages in the proper hierarchy as specified.
"""
from django.core.management.base import BaseCommand
from wagtail.models import Page
from home.models import HomePage, AboutPage, ContentPage


class Command(BaseCommand):
    help = 'Sets up the complete lyceum site structure'

    def ensure_page(self, parent, page_class, slug, title, **kwargs):
        page = page_class.objects.child_of(parent).filter(slug=slug).specific().first()
        if page:
            page.title = title
            for field, value in kwargs.items():
                setattr(page, field, value)
            page.save_revision().publish()
            self.stdout.write(f"  ✓ Updated {title}")
            return page

        page = page_class(title=title, slug=slug, show_in_menus=True, **kwargs)
        parent.add_child(instance=page)
        page.save_revision().publish()
        self.stdout.write(f"  ✓ Created {title}")
        return page

    def handle(self, *args, **options):
        self.stdout.write("Creating site structure...")

        # Get the Wagtail root page
        try:
            root = Page.get_first_root_node()
        except Page.DoesNotExist:
            self.stdout.write(self.style.ERROR("ERROR: No Wagtail root page found. Run migrations first."))
            return

        # Create or get HomePage as a child of root
        home = HomePage.objects.first()
        if not home:
            home = HomePage(
                title="Головна",
                slug="home",
                show_in_menus=True,
            )
            root.add_child(instance=home)
            home.save()
            self.stdout.write(self.style.SUCCESS("✓ Created HomePage"))
        else:
            self.stdout.write("HomePage already exists")
            # Delete all children to start fresh
            for child in home.get_children():
                child.delete()
            self.stdout.write("Cleared existing pages")

        # 1. About Section
        about = self.ensure_page(
            home,
            AboutPage,
            "about",
            "Про ліцей",
            subtitle="Дізнайтеся більше про наш заклад",
            intro="Ліцей є закладом, що надає якісну освіту...",
        )

        # About subsections
        about_subsections = [
            ("Історія ліцею", "history"),
            ("Керівництво ліцею", "management"),
            ("Педагогічний колектив", "pedagogical-staff"),
            ("Соціально-психологічна служба", "psychological-service"),
        ]
        for title, slug in about_subsections:
            self.ensure_page(
                about,
                ContentPage,
                slug,
                title,
                body=f"<p>Вміст сторінки про {title}</p>",
            )

        # 2. Create all content sections as universal ContentPage instances
        content_sections = [
            (home, "Публічна інформація", "public-information", "<p>Інформація про Публічна інформація</p>"),
            (home, "Освітній процес", "educational-process", "<p>Інформація про Освітній процес</p>"),
            (home, "Виховна робота", "educational-work", "<p>Інформація про Виховна робота</p>"),
            (home, "Батькам", "parents", "<p>Ласкаво просимо на сторінку для батьків. Тут ви знайдете корисну інформацію...</p>"),
            (home, "Педагогам", "teachers", "<p>Ласкаво просимо на сторінку для педагогів. Тут ви знайдете корисні ресурси...</p>"),
            (home, "Контакти", "contacts", "<p>Зв'яжіться з нами:</p>"),
        ]

        for parent, title, slug, body in content_sections:
            self.ensure_page(
                parent,
                ContentPage,
                slug,
                title,
                body=body,
            )

        self.stdout.write(self.style.SUCCESS("\n✅ Site structure created successfully!"))
        self.stdout.write("\nPage hierarchy:")
        self.stdout.write("  Головна")
        self.stdout.write("  ├── Про ліцей")
        self.stdout.write("  │   ├── Історія ліцею")
        self.stdout.write("  │   ├── Керівництво ліцею")
        self.stdout.write("  │   ├── Педагогічний колектив")
        self.stdout.write("  │   └── Соціально-психологічна служба")
        self.stdout.write("  ├── Історія ліцею")
        self.stdout.write("  ├── Керівництво ліцею")
        self.stdout.write("  ├── Педагогічний колектив")
        self.stdout.write("  ├── Соціально-психологічна служба")
        self.stdout.write("  ├── Публічна інформація")
        self.stdout.write("  ├── Освітній процес")
        self.stdout.write("  ├── Виховна робота")
        self.stdout.write("  ├── Батькам")
        self.stdout.write("  ├── Педагогам")
        self.stdout.write("  └── Контакти")
