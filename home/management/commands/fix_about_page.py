from django.core.management.base import BaseCommand
from home.models import HomePage, AboutPage

class Command(BaseCommand):
    help = 'Fixes the About page - moves it from Staff to Home'

    def handle(self, *args, **options):
        # Create new AboutPage under Home if it doesn't exist
        home = HomePage.objects.first()
        if not home:
            self.stdout.write(self.style.ERROR("HomePage not found"))
            return

        if not AboutPage.objects.filter(slug='about').exists():
            about_page = AboutPage(
                title="Про ліцей",
                body="<p>Миколаївський ліцей №9 — сучасний освітній заклад для обдарованої молоді.</p>",
                slug="about"
            )
            home.add_child(instance=about_page)
            about_page.save_revision().publish()
            self.stdout.write(self.style.SUCCESS("Created new AboutPage under Home"))
        else:
            self.stdout.write("AboutPage already exists under Home")

        self.stdout.write(self.style.SUCCESS("Fix complete!"))
