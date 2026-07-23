from django.core.management.base import BaseCommand
from wagtail.models import Page, Site


class Command(BaseCommand):
    help = 'Creates the default About page if it does not exist'

    def handle(self, *args, **options):
        from home.models import AboutPage, HomePage
        
        # Get the home page
        try:
            site = Site.objects.get(is_default_site=True)
            home_page = site.root_page.specific
            if not isinstance(home_page, HomePage):
                home_page = HomePage.objects.first()
        except Site.DoesNotExist:
            home_page = HomePage.objects.first()
        
        if not home_page:
            self.stdout.write(self.style.ERROR('No HomePage found. Please create one first.'))
            return

        about_page = AboutPage.objects.first()
        if about_page:
            about_page.title = "Про нас"
            about_page.slug = "about"
            about_page.subtitle = "Освіта для майбутнього"
            about_page.show_in_menus = True

            if about_page.get_parent().id != home_page.id:
                about_page.move(home_page, pos="last-child")

            about_page.save_revision().publish()
            self.stdout.write(self.style.SUCCESS('Successfully updated About page at /about/'))
            return

        about_page = AboutPage(
            title="Про нас",
            slug="about",
            subtitle="Освіта для майбутнього",
            show_in_menus=True,
        )

        home_page.add_child(instance=about_page)
        about_page.save_revision().publish()

        self.stdout.write(self.style.SUCCESS('Successfully created About page at /about/'))
