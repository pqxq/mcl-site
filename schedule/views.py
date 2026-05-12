from collections import Counter

from django.shortcuts import render

from .models import LESSON_TIMES, ClassGroup, Day, Lesson, Week

PARA_BY_LESSON_NUMBER = {
    1: "I",
    2: "I",
    3: "II",
    4: "II",
    5: "III",
    6: "III",
    7: "IV",
    8: "IV",
}


def normalize_week_filter(value):
    valid_weeks = {str(number) for number, _ in Week.choices}
    if value in valid_weeks:
        return value
    return "1"


def get_lesson_numbers(para_number, para_part):
    first_lesson = para_number * 2 - 1
    second_lesson = para_number * 2
    if para_part == 0:
        return [first_lesson, second_lesson]
    if para_part == 1:
        return [first_lesson]
    return [second_lesson]


def annotate_para_headers(sorted_rows):
    para_rowspans = Counter(row["para"] for row in sorted_rows.values())
    last_para = None
    for row in sorted_rows.values():
        is_new_para = row["para"] != last_para
        row["show_para"] = is_new_para
        if is_new_para:
            row["para_rowspan"] = para_rowspans[row["para"]]
            last_para = row["para"]


def build_schedule_data(lessons):
    lessons_by_day = {}
    for lesson in lessons:
        lessons_by_day.setdefault(lesson.day, []).append(lesson)

    schedule_data = {}
    for day_number, day_name in Day.choices:
        day_lessons = lessons_by_day.get(day_number, [])
        if not day_lessons:
            continue

        lessons_by_number = {}
        for lesson in day_lessons:
            lesson_numbers = get_lesson_numbers(lesson.para_number, lesson.para_part)
            for index, lesson_number in enumerate(lesson_numbers):
                row = lessons_by_number.setdefault(
                    lesson_number,
                    {
                        "time": LESSON_TIMES.get(lesson_number, ""),
                        "para": PARA_BY_LESSON_NUMBER.get(lesson_number, ""),
                        "lessons": {},
                    },
                )

                class_lessons = row["lessons"].setdefault(lesson.class_group_id, [])
                class_lessons.append(
                    {
                        "subject": lesson.subject,
                        "cabinet": lesson.cabinet,
                        "sub_group": lesson.sub_group,
                        "rowspan": 2 if lesson.para_part == 0 and index == 0 else 1,
                        "skip": lesson.para_part == 0 and index == 1,
                    }
                )

        sorted_rows = dict(sorted(lessons_by_number.items()))
        annotate_para_headers(sorted_rows)
        schedule_data[day_name] = sorted_rows

    return schedule_data


def schedule_view(request):
    """Display the schedule/timetable page."""
    week_filter = normalize_week_filter(request.GET.get("week"))
    class_groups = ClassGroup.objects.order_by("name", "study_type")
    lessons = list(
        Lesson.objects.select_related("subject", "class_group")
        .filter(week=int(week_filter))
        .order_by("day", "para_number", "para_part", "class_group__name")
    )

    context = {
        "schedule_data": build_schedule_data(lessons),
        "class_groups": class_groups,
        "current_week": week_filter,
    }
    return render(request, "schedule/schedule_page.html", context)
