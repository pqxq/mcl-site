from django.core.management.base import BaseCommand
from wagtail.models import Page, Site


class Command(BaseCommand):
    help = 'Creates the default About page if it does not exist'

    def handle(self, *args, **options):
        from home.models import AboutPage, HomePage
        
        # Check if AboutPage already exists
        if AboutPage.objects.exists():
            self.stdout.write(self.style.WARNING('About page already exists'))
            return
        
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
        
        # Create the About page
        about_page = AboutPage(
            title="Про нас",
            slug="about",
            subtitle="Освіта для майбутнього",
            show_in_menus=True,
        )
        
        home_page.add_child(instance=about_page)
        about_page.save_revision().publish()
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created About page at /about/'))
