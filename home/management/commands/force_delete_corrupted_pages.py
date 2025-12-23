from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Force delete corrupted pages directly from database'

    def handle(self, *args, **options):
        page_ids = [8, 9, 10]
        
        self.stdout.write(f'Force deleting pages: {page_ids}')
        
        with connection.cursor() as cursor:
            # Disable foreign key checks for SQLite
            cursor.execute("PRAGMA foreign_keys = OFF")
            
            # Delete from wagtailcore_page table directly
            for page_id in page_ids:
                try:
                    sql = f"DELETE FROM wagtailcore_page WHERE id = {page_id}"
                    cursor.execute(sql)
                    self.stdout.write(self.style.SUCCESS(f'Deleted page {page_id}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error deleting page {page_id}: {e}'))
            
            # Re-enable foreign key checks
            cursor.execute("PRAGMA foreign_keys = ON")
        
        self.stdout.write(self.style.SUCCESS('Done!'))

