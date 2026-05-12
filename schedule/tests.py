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
