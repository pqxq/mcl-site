from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.core.files.base import ContentFile
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from news.models import NewsPage
from home.models import HomePage
from wagtail.models import Page
import time

class Command(BaseCommand):
    help = 'Scrapes news from mcl.mk.ua and imports into Wagtail'

    def handle(self, *args, **options):
        base_url = "https://mcl.mk.ua/"
        self.stdout.write(f"Scraping {base_url}...")

        try:
            response = requests.get(base_url, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find the Home Page to attach news to
            home_page = HomePage.objects.first()
            if not home_page:
                self.stdout.write(self.style.ERROR("HomePage not found! Please run migrations/setup first."))
                return

            # Example selector - this needs to be adjusted based on actual site structure
            # Based on previous read_url_content, effective main content seems to be in standard WP structure
            articles = soup.find_all('article')
            
            count = 0
            for article in articles:
                # Extract Title
                title_elem = article.find('h2') or article.find('h1')
                if not title_elem:
                    continue
                title = title_elem.get_text(strip=True)
                
                # Check if exists
                if NewsPage.objects.filter(title=title).exists():
                    self.stdout.write(f"Skipping {title} (already exists)")
                    continue

                # Extract content
                content_div = article.find('div', class_='entry-content') or article.find('div', class_='post-content')
                body_html = str(content_div) if content_div else ""
                
                # Extract date if available (often in time tag or specific class)
                date_str = datetime.now().date() # Default
                
                # Create Page
                news_page = NewsPage(
                    title=title,
                    intro=body_html[:100] + "...", # Simple truncation for intro
                    body=body_html,
                    date=date_str,
                    slug=slugify(title)[:50] # truncated slug
                )
                
                home_page.add_child(instance=news_page)
                news_page.save_revision().publish()
                
                self.stdout.write(self.style.SUCCESS(f"Imported: {title}"))
                count += 1
                time.sleep(0.5) # Be polite

            self.stdout.write(self.style.SUCCESS(f"Successfully imported {count} articles."))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error scraping: {e}"))
