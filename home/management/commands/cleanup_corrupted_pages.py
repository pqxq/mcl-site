from django.core.management.base import BaseCommand
from wagtail.models import Page
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = 'Remove corrupted LogEntry and IndexEntry pages from the Page table'

    def handle(self, *args, **options):
        # Find LogEntry content type
        log_entry_ct = ContentType.objects.filter(
            app_label='wagtailcore', 
            model='logentry'
        ).first()
        
        if log_entry_ct:
            bad_pages = Page.objects.filter(content_type=log_entry_ct)
            count = bad_pages.count()
            if count > 0:
                self.stdout.write(f'Found {count} LogEntry pages to delete')
                for page in bad_pages:
                    self.stdout.write(f'  Deleting: ID {page.id} - {page.title}')
                    page.delete()
                self.stdout.write(self.style.SUCCESS(f'Deleted {count} LogEntry pages'))
            else:
                self.stdout.write('No LogEntry pages found')
        else:
            self.stdout.write('LogEntry content type not found')
        
        # Find IndexEntry content type
        index_entry_ct = ContentType.objects.filter(
            app_label='wagtailsearch', 
            model='indexentry'
        ).first()
        
        if index_entry_ct:
            bad_pages = Page.objects.filter(content_type=index_entry_ct)
            count = bad_pages.count()
            if count > 0:
                self.stdout.write(f'Found {count} IndexEntry pages to delete')
                # Change content_type to a valid page type first, then delete
                from home.models import HomePage
                home_page_ct = ContentType.objects.get_for_model(HomePage)
                
                for page_id in list(bad_pages.values_list('id', flat=True)):
                    try:
                        # Update content_type to HomePage so we can delete it
                        Page.objects.filter(id=page_id).update(content_type=home_page_ct)
                        # Now delete it
                        Page.objects.filter(id=page_id).delete()
                        self.stdout.write(self.style.SUCCESS(f'  Deleted page {page_id}'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'  Could not delete page {page_id}: {e}'))
            else:
                self.stdout.write('No IndexEntry pages found')
        else:
            self.stdout.write('IndexEntry content type not found')
        
        # Also check for LogEntry by model name
        log_entry_ct_by_name = ContentType.objects.filter(
            model='logentry'
        ).first()
        
        if log_entry_ct_by_name:
            bad_pages = Page.objects.filter(content_type=log_entry_ct_by_name)
            count = bad_pages.count()
            if count > 0:
                self.stdout.write(f'Found {count} LogEntry pages to delete (by name)')
                from home.models import HomePage
                home_page_ct = ContentType.objects.get_for_model(HomePage)
                
                for page_id in list(bad_pages.values_list('id', flat=True)):
                    try:
                        # Update content_type to HomePage so we can delete it
                        Page.objects.filter(id=page_id).update(content_type=home_page_ct)
                        # Now delete it
                        Page.objects.filter(id=page_id).delete()
                        self.stdout.write(self.style.SUCCESS(f'  Deleted page {page_id}'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'  Could not delete page {page_id}: {e}'))
        
        # Show remaining pages
        remaining = Page.objects.all()
        self.stdout.write(f'\nRemaining pages: {remaining.count()}')
        for page in remaining:
            self.stdout.write(f'  ID: {page.id}, Title: {page.title}, Type: {page.content_type}')
