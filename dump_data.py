"""Dump data from SQLite with proper UTF-8 encoding."""
import os
import sys
import io

# Force UTF-8 output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mcl_site.settings.dev')

import django
django.setup()

from django.core.management import call_command

with open('datadump.json', 'w', encoding='utf-8') as f:
    call_command(
        'dumpdata',
        '--natural-foreign',
        '--natural-primary',
        '--indent', '2',
        '-e', 'contenttypes',
        '-e', 'auth.Permission',
        '-e', 'sessions',
        stdout=f
    )

print("Data dump complete! Saved to datadump.json")
