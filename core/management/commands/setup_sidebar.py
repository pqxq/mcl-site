"""
Django management command to set up the sidebar navigation structure.
"""
from django.core.management.base import BaseCommand
from wagtail.models import Page
from core.models import SidebarSection, SidebarLink


class Command(BaseCommand):
    help = 'Sets up the sidebar navigation structure'

    def handle(self, *args, **options):
        self.stdout.write("Setting up sidebar navigation...")
        
        # Clear existing sidebar sections
        SidebarSection.objects.all().delete()
        self.stdout.write("Cleared existing sidebar sections")
        
        # Get pages by slug for easier reference
        pages = {}
        for page in Page.objects.all():
            pages[page.slug] = page
        
        # Helper function to get page by title
        def get_page(title):
            page = Page.objects.filter(title=title).first()
            return page
        
        order_counter = 10
        
        # 1. Головна
        home_page = get_page("Home")
        if home_page:
            section = SidebarSection.objects.create(
                title="Головна",
                icon="bi-house",
                order=order_counter,
                is_expanded=False
            )
            SidebarLink.objects.create(
                section=section,
                label="Головна",
                page=home_page,
                sort_order=0
            )
            self.stdout.write(f"✓ Created section: Головна")
            order_counter += 10
        
        # 2. Про ліцей
        about_page = get_page("Про ліцей")
        if about_page:
            section = SidebarSection.objects.create(
                title="Про ліцей",
                icon="bi-info-circle",
                order=order_counter,
                is_expanded=True
            )
            self.stdout.write(f"✓ Created section: Про ліцей")
            
            about_links = [
                ("Історія ліцею", "history"),
                ("Керівництво ліцею", "management"),
                ("Педагогічний колектив", "pedagogical-staff"),
                ("Соціально-психологічна служба", "psychological-service"),
            ]
            
            for idx, (label, slug) in enumerate(about_links):
                link_page = get_page(label)
                if link_page:
                    SidebarLink.objects.create(
                        section=section,
                        label=label,
                        page=link_page,
                        sort_order=idx
                    )
                    self.stdout.write(f"  ✓ Added: {label}")
            order_counter += 10
        
        # 3. Публічна інформація
        public_info_page = get_page("Публічна інформація")
        if public_info_page:
            section = SidebarSection.objects.create(
                title="Публічна інформація",
                icon="bi-file-text",
                order=order_counter,
                is_expanded=True
            )
            self.stdout.write(f"✓ Created section: Публічна інформація")
            
            public_links = [
                ("Установчі документи", "charter"),
                ("Нормативні документи", "normative-documents"),
                ("Фінансова діяльність", "financial-activity"),
                ("Положення", "regulations"),
                ("Якість освіти", "education-quality"),
                ("Безпека життєдіяльності", "life-safety"),
                ("Профілактика булінгу та жорстокого поводження", "bullying-prevention"),
                ("Вступ до ліцею", "admission"),
                ("Інклюзія", "inclusion"),
            ]
            
            for idx, (label, slug) in enumerate(public_links):
                link_page = get_page(label)
                if link_page:
                    SidebarLink.objects.create(
                        section=section,
                        label=label,
                        page=link_page,
                        sort_order=idx
                    )
                    self.stdout.write(f"  ✓ Added: {label}")
            order_counter += 10
        
        # 4. Освітній процес
        edu_process_page = get_page("Освітній процес")
        if edu_process_page:
            section = SidebarSection.objects.create(
                title="Освітній процес",
                icon="bi-book",
                order=order_counter,
                is_expanded=True
            )
            self.stdout.write(f"✓ Created section: Освітній процес")

            # Розклад links to the dedicated schedule Django view, not a CMS page
            SidebarLink.objects.create(
                section=section,
                label="Розклад",
                external_url="/schedule/",
                sort_order=0
            )
            self.stdout.write(f"  ✓ Added: Розклад → /schedule/")

            edu_links = [
                ("Критерії оцінювання з предметів", "grading-criteria"),
                ("Досягнення", "achievements"),
                ("Все про НМТ (ЗНО)", "nmt-info"),
            ]
            
            for idx, (label, slug) in enumerate(edu_links, start=1):
                link_page = get_page(label)
                if link_page:
                    SidebarLink.objects.create(
                        section=section,
                        label=label,
                        page=link_page,
                        sort_order=idx
                    )
                    self.stdout.write(f"  ✓ Added: {label}")
            order_counter += 10
        
        # 5. Виховна робота
        work_page = get_page("Виховна робота")
        if work_page:
            section = SidebarSection.objects.create(
                title="Виховна робота",
                icon="bi-people",
                order=order_counter,
                is_expanded=True
            )
            self.stdout.write(f"✓ Created section: Виховна робота")
            
            work_links = [
                ("Учнівське самоврядування", "student-government"),
                ("Патріотичне виховання", "patriotic-education"),
                ("Безбар'єрність", "accessibility"),
            ]
            
            for idx, (label, slug) in enumerate(work_links):
                link_page = get_page(label)
                if link_page:
                    SidebarLink.objects.create(
                        section=section,
                        label=label,
                        page=link_page,
                        sort_order=idx
                    )
                    self.stdout.write(f"  ✓ Added: {label}")
            order_counter += 10
        
        # 6. Батькам
        parents_page = get_page("Батькам")
        if parents_page:
            section = SidebarSection.objects.create(
                title="Батькам",
                icon="bi-heart",
                order=order_counter,
                is_expanded=False
            )
            SidebarLink.objects.create(
                section=section,
                label="Батькам",
                page=parents_page,
                sort_order=0
            )
            self.stdout.write(f"✓ Created section: Батькам")
            order_counter += 10
        
        # 7. Педагогам
        teachers_page = get_page("Педагогам")
        if teachers_page:
            section = SidebarSection.objects.create(
                title="Педагогам",
                icon="bi-mortarboard",
                order=order_counter,
                is_expanded=False
            )
            SidebarLink.objects.create(
                section=section,
                label="Педагогам",
                page=teachers_page,
                sort_order=0
            )
            self.stdout.write(f"✓ Created section: Педагогам")
            order_counter += 10
        
        # 8. Новини
        news_page = Page.objects.filter(title="Новини").first()
        if news_page:
            section = SidebarSection.objects.create(
                title="Новини",
                icon="bi-newspaper",
                order=order_counter,
                is_expanded=False
            )
            SidebarLink.objects.create(
                section=section,
                label="Новини",
                page=news_page,
                sort_order=0
            )
            self.stdout.write(f"✓ Created section: Новини")
            order_counter += 10
        
        # 9. Контакти
        contacts_page = get_page("Контакти")
        if contacts_page:
            section = SidebarSection.objects.create(
                title="Контакти",
                icon="bi-telephone",
                order=order_counter,
                is_expanded=False
            )
            SidebarLink.objects.create(
                section=section,
                label="Контакти",
                page=contacts_page,
                sort_order=0
            )
            self.stdout.write(f"✓ Created section: Контакти")
            order_counter += 10
        
        # 10. Галерея
        gallery_page = get_page("Галерея")
        if gallery_page:
            section = SidebarSection.objects.create(
                title="Галерея",
                icon="bi-images",
                order=order_counter,
                is_expanded=False
            )
            SidebarLink.objects.create(
                section=section,
                label="Галерея",
                page=gallery_page,
                sort_order=0
            )
            self.stdout.write(f"✓ Created section: Галерея")
        
        self.stdout.write(self.style.SUCCESS("\n✅ Sidebar navigation set up successfully!"))
        self.stdout.write("\nSidebar structure:")
        self.stdout.write("  Головна")
        self.stdout.write("  Про ліцей")
        self.stdout.write("    - Історія ліцею")
        self.stdout.write("    - Керівництво ліцею")
        self.stdout.write("    - Педагогічний колектив")
        self.stdout.write("    - Соціально-психологічна служба")
        self.stdout.write("  Публічна інформація")
        self.stdout.write("    - Установчі документи")
        self.stdout.write("    - Нормативні документи")
        self.stdout.write("    - Фінансова діяльність")
        self.stdout.write("    - Положення")
        self.stdout.write("    - Якість освіти")
        self.stdout.write("    - Безпека життедіяльності")
        self.stdout.write("    - Профілактика булінгу та жорстокого поводження")
        self.stdout.write("    - Вступ до ліцею")
        self.stdout.write("    - Інклюзія")
        self.stdout.write("  Освітній процес")
        self.stdout.write("    - Критерії оцінювання з предметів")
        self.stdout.write("    - Досягнення")
        self.stdout.write("    - Все про НМТ (ЗНО)")
        self.stdout.write("  Виховна робота")
        self.stdout.write("    - Учнівське самоврядування")
        self.stdout.write("    - Патріотичне виховання")
        self.stdout.write("    - Безбар'єрність")
        self.stdout.write("  Батькам")
        self.stdout.write("  Педагогам")
        self.stdout.write("  Новини")
        self.stdout.write("  Контакти")
        self.stdout.write("  Галерея")
