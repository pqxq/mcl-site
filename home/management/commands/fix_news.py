from django.core.management.base import BaseCommand
from wagtail.models import Page
from home.models import HomePage
from news.models import NewsIndexPage, NewsPage


class Command(BaseCommand):
    help = 'Fixes the news page structure by cleaning up and creating proper pages'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force recreation of NewsIndexPage even if one exists',
        )

    def handle(self, *args, **options):
        home = HomePage.objects.first()
        if not home:
            self.stdout.write(self.style.ERROR("HomePage not found."))
            return

        # Delete any NewsPage that is direct child of HomePage (wrong structure)
        wrong_news = NewsPage.objects.child_of(home)
        if wrong_news.exists():
            for page in wrong_news:
                self.stdout.write(f"Deleting incorrectly placed NewsPage: {page.title}")
                page.delete()

        # Check for NewsIndexPage
        news_indexes = NewsIndexPage.objects.child_of(home)
        
        if options['force'] and news_indexes.exists():
            for ni in news_indexes:
                self.stdout.write(f"Force deleting NewsIndexPage: {ni.title}")
                ni.delete()
            news_indexes = NewsIndexPage.objects.none()
        
        if not news_indexes.exists():
            # Create new NewsIndexPage with correct slug
            news_index = NewsIndexPage(
                title="Новини",
                intro="<p>Останні новини та події ліцею</p>",
                slug="news"
            )
            home.add_child(instance=news_index)
            news_index.save_revision().publish()
            self.stdout.write(self.style.SUCCESS("Created NewsIndexPage 'Новини' at /news/"))
        else:
            # Fix existing NewsIndexPage slug and title
            news_index = news_indexes.first()
            if news_index.slug != 'news' or news_index.title != 'Новини':
                news_index.title = "Новини"
                news_index.slug = "news"
                news_index.save_revision().publish()
                self.stdout.write(self.style.SUCCESS(f"Updated NewsIndexPage to 'Новини' at /news/"))
            else:
                self.stdout.write(self.style.SUCCESS(f"NewsIndexPage already correct: {news_index.title} at /{news_index.slug}/"))

        self.stdout.write(self.style.SUCCESS("\n✓ News structure fixed!"))
        self.stdout.write("\nTo add news articles:")
        self.stdout.write("1. Go to /admin/")
        self.stdout.write("2. Click 'Pages' in sidebar")
        self.stdout.write("3. Navigate to Home -> Новини")
        self.stdout.write("4. Click '+ Add child page' and select 'Новина'")
