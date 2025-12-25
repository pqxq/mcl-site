import csv
from typing import Optional

from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify

from wagtail.contrib.redirects.models import Redirect
from wagtail.models import Site


class Command(BaseCommand):
    help = "Import redirects from a CSV with columns: old_path,new_path[,is_permanent]"

    def add_arguments(self, parser):
        parser.add_argument('csv_path', type=str, help='Path to the CSV file')
        parser.add_argument('--site', type=int, default=None, help='Wagtail Site ID (defaults to default site)')
        parser.add_argument('--dry-run', action='store_true', help='Print actions without saving')

    def _get_site(self, site_id: Optional[int]) -> Site:
        if site_id is not None:
            try:
                return Site.objects.get(id=site_id)
            except Site.DoesNotExist:
                raise CommandError(f"Site with id={site_id} not found")
        site = Site.objects.filter(is_default_site=True).first()
        if not site:
            raise CommandError("Default site not configured")
        return site

    def handle(self, *args, **options):
        csv_path: str = options['csv_path']
        site: Site = self._get_site(options.get('site'))
        dry_run: bool = options['dry_run']

        created = 0
        updated = 0

        try:
            with open(csv_path, newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                for i, row in enumerate(reader, start=1):
                    if not row or row[0].strip().startswith('#'):
                        continue
                    if len(row) < 2:
                        self.stderr.write(f"Row {i}: expected at least 2 columns (old_path,new_path)")
                        continue
                    old_path = row[0].strip()
                    new_path = row[1].strip()
                    is_permanent = True
                    if len(row) >= 3:
                        val = row[2].strip().lower()
                        is_permanent = val in ('1', 'true', 'yes', 'y', 'permanent', '301')

                    # Normalize paths to start with '/'
                    if not old_path.startswith('/'):
                        old_path = '/' + old_path
                    if not new_path.startswith('/') and not new_path.startswith('http'):
                        new_path = '/' + new_path

                    redirect, created_flag = Redirect.objects.update_or_create(
                        old_path=old_path,
                        site=site,
                        defaults={
                            'redirect_link': new_path,
                            'is_permanent': is_permanent,
                        }
                    )
                    if dry_run:
                        action = 'CREATE' if created_flag else 'UPDATE'
                        self.stdout.write(f"{action} {old_path} -> {new_path} (permanent={is_permanent})")
                    else:
                        if created_flag:
                            created += 1
                        else:
                            updated += 1
        except FileNotFoundError:
            raise CommandError(f"CSV file not found: {csv_path}")

        if not dry_run:
            self.stdout.write(self.style.SUCCESS(f"Imported redirects: created={created}, updated={updated}"))
