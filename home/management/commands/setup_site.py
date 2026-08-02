from django.core.management.base import BaseCommand
from wagtail.models import Page
from home.models import HomePage, AboutPage
from news.models import NewsIndexPage, NewsPage
from admissions.models import ApplicationFormPage
from staff.models import StaffIndexPage


class Command(BaseCommand):
    help = 'Creates initial site structure'

    def handle(self, *args, **options):
        # 1. Create or get Home Page
        home = HomePage.objects.first()
        if not home:
            # Get the root page
            root = Page.get_root_nodes().first()
            home = HomePage(
                title="Головна",
                slug="home"
            )
            root.add_child(instance=home)
            home.save_revision().publish()
            self.stdout.write(self.style.SUCCESS("Created Home Page (home)"))
        else:
            self.stdout.write("Home Page already exists")

        # 2. Create News Index Page
        if not NewsIndexPage.objects.descendant_of(home).exists():
            news_index = NewsIndexPage(
                title="Новини",
                intro="<p>Останні новини та події нашого ліцею</p>",
                slug="news"
            )
            home.add_child(instance=news_index)
            news_index.save_revision().publish()
            self.stdout.write(self.style.SUCCESS("Created News Index Page (news)"))
        else:
            self.stdout.write("News Index already exists")

        # 3. Create Admissions Page
        admissions_page = ApplicationFormPage.objects.descendant_of(home).first()
        if not admissions_page:
            admissions_page = ApplicationFormPage(
                title="Вступ",
                intro="<p>Заповніть анкету для вступу до ліцею.</p>",
                thank_you_text="<p>Дякуємо! Ваша заявка прийнята. Ми зв'яжемося з вами найближчим часом.</p>",
                slug="admissions"
            )
            home.add_child(instance=admissions_page)
            admissions_page.save_revision().publish()
            self.stdout.write(self.style.SUCCESS("Created Admissions Page (admissions)"))
        else:
            self.stdout.write("Admissions Page already exists")

        if admissions_page and admissions_page.form_fields.count() == 0:
            from admissions.models import FormField
            default_fields = [
                ("ПІБ дитини", "singleline", True, "Прізвище, ім'я та по батькові дитини"),
                ("Дата народження дитини", "date", True, "Дата народження майбутнього ліцеїста"),
                ("Клас, до якого вступає дитина", "dropdown", True, ""),
                ("ПІБ одного з батьків / опікуна", "singleline", True, "Прізвище, ім'я та по батькові батьків"),
                ("Контактний телефон", "singleline", True, "Номер телефону для зв'язку (+380...)"),
                ("Електронна пошта", "email", False, "Адреса електронної пошти"),
                ("Фото або скан підписаної заяви", "file", True, "Завантажте фото або скан-копію заповненої та підписаної заяви за зразком (JPG, PNG, PDF)"),
            ]
            for label, ftype, req, help_txt in default_fields:
                choices = "1 клас, 5 клас, 10 клас" if ftype == "dropdown" else ""
                FormField.objects.create(
                    page=admissions_page,
                    label=label,
                    field_type=ftype,
                    required=req,
                    choices=choices,
                    help_text=help_txt
                )
            admissions_page.save_revision().publish()
            self.stdout.write(self.style.SUCCESS("Populated default form fields for Admissions Page"))


        # 4. Create About Page
        if not AboutPage.objects.filter(slug='about').exists():
            about_page = AboutPage(
                title="Про ліцей",
                subtitle="Миколаївський ліцей №9 — сучасний освітній заклад для обдарованої молоді",
                slug="about"
            )
            home.add_child(instance=about_page)
            about_page.save_revision().publish()
            self.stdout.write(self.style.SUCCESS("Created About Page (about)"))
        else:
            self.stdout.write("About Page already exists")

        # 5. Create Staff Index Page
        if not StaffIndexPage.objects.descendant_of(home).exists():
            staff_index = StaffIndexPage(
                title="Колектив",
                intro="<p>Познайомтесь із нашою командою професіоналів</p>",
                slug="staff"
            )
            home.add_child(instance=staff_index)
            staff_index.save_revision().publish()
            self.stdout.write(self.style.SUCCESS("Created Staff Index Page (staff)"))
        else:
            self.stdout.write("Staff Index already exists")

        self.stdout.write(self.style.SUCCESS("\nSetup complete! Visit /admin/ to manage content."))
