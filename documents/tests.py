from django.test import SimpleTestCase
from django.utils import timezone

from .models import current_year


class DocumentsModelHelpersTests(SimpleTestCase):
    def test_current_year_matches_timezone_year(self):
        self.assertEqual(current_year(), timezone.now().year)
