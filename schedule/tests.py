from dataclasses import dataclass

from django.test import SimpleTestCase

from .models import Day
from .views import build_schedule_data, get_lesson_numbers, normalize_week_filter


@dataclass
class FakeLesson:
    day: int
    para_number: int
    para_part: int
    class_group_id: int
    subject: str
    cabinet: str = ""
    sub_group: int = 0


class ScheduleViewHelpersTests(SimpleTestCase):
    def test_normalize_week_filter(self):
        self.assertEqual(normalize_week_filter("1"), "1")
        self.assertEqual(normalize_week_filter("4"), "4")
        self.assertEqual(normalize_week_filter("0"), "1")
        self.assertEqual(normalize_week_filter("bad"), "1")
        self.assertEqual(normalize_week_filter(None), "1")

    def test_get_lesson_numbers(self):
        self.assertEqual(get_lesson_numbers(1, 0), [1, 2])
        self.assertEqual(get_lesson_numbers(2, 1), [3])
        self.assertEqual(get_lesson_numbers(3, 2), [6])

    def test_build_schedule_data(self):
        monday_name = Day.choices[0][1]
        schedule_data = build_schedule_data(
            [
                FakeLesson(
                    day=Day.MONDAY,
                    para_number=1,
                    para_part=0,
                    class_group_id=1,
                    subject="Math",
                    cabinet="101",
                ),
                FakeLesson(
                    day=Day.MONDAY,
                    para_number=2,
                    para_part=1,
                    class_group_id=2,
                    subject="Chemistry",
                    cabinet="202",
                ),
            ]
        )

        self.assertIn(monday_name, schedule_data)
        monday_rows = schedule_data[monday_name]
        self.assertEqual(list(monday_rows.keys()), [1, 2, 3])

        first_row = monday_rows[1]
        second_row = monday_rows[2]
        third_row = monday_rows[3]

        self.assertEqual(first_row["para"], "I")
        self.assertTrue(first_row["show_para"])
        self.assertEqual(first_row["para_rowspan"], 2)
        self.assertEqual(first_row["lessons"][1][0]["rowspan"], 2)
        self.assertFalse(first_row["lessons"][1][0]["skip"])

        self.assertFalse(second_row["show_para"])
        self.assertTrue(second_row["lessons"][1][0]["skip"])

        self.assertEqual(third_row["para"], "II")
        self.assertTrue(third_row["show_para"])
        self.assertEqual(third_row["para_rowspan"], 1)
        self.assertEqual(third_row["lessons"][2][0]["subject"], "Chemistry")


from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from wagtail.models import Site
from wagtail.documents.models import Document
from .models import ScheduleSettings


class ScheduleSettingsTests(TestCase):
    def setUp(self):
        cache.clear()
        self.site = Site.objects.filter(is_default_site=True).first()
        if not self.site:
            self.site = Site.objects.create(
                hostname="localhost",
                port=80,
                site_name="Test Site",
                is_default_site=True,
                root_page_id=1,
            )

        self.doc1 = Document.objects.create(
            title="Структура 2026",
            file=SimpleUploadedFile("structure_2026.pdf", b"%PDF-1.4 test document content"),
        )
        self.doc2 = Document.objects.create(
            title="Тижні 2026",
            file=SimpleUploadedFile("weeks_2026.pdf", b"%PDF-1.4 test document content"),
        )

    def tearDown(self):
        cache.clear()


    def test_schedule_settings_str(self):
        settings = ScheduleSettings.objects.create(
            site=self.site,
            academic_year_structure_doc=self.doc1,
            semester_weeks_doc=self.doc2,
        )
        self.assertEqual(str(settings), "Налаштування розкладу та документи")
        self.assertEqual(settings.academic_year_structure_title, "Структура навчального року")
        self.assertEqual(settings.semester_weeks_title, "Тижні семестру навчального року")

    def test_schedule_page_without_documents(self):
        response = self.client.get(reverse("schedule"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Загальнонаціональна хвилина мовчання")
        self.assertNotContains(response, "schedule-documents")

    def test_schedule_page_with_attached_documents(self):
        ScheduleSettings.objects.create(
            site=self.site,
            academic_year_structure_doc=self.doc1,
            semester_weeks_doc=self.doc2,
        )

        response = self.client.get(reverse("schedule"))
        self.assertEqual(response.status_code, 200)

        content = response.content.decode("utf-8")
        self.assertIn("schedule-documents", content)
        self.assertIn("Структура навчального року", content)
        self.assertIn("Тижні семестру навчального року", content)
        self.assertIn(self.doc1.url, content)
        self.assertIn(self.doc2.url, content)
        self.assertIn("Загальнонаціональна хвилина мовчання", content)

        # Verify documents appear BEFORE the 9:00 minute of silence notice
        doc_pos = content.index("schedule-documents")
        notice_pos = content.index("schedule-notice")
        silence_pos = content.index("Загальнонаціональна хвилина мовчання")
        self.assertLess(doc_pos, notice_pos)
        self.assertLess(doc_pos, silence_pos)

