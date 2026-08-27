from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet


@register_snippet
class Subject(models.Model):
    name = models.CharField("Предмет", max_length=100)

    class Meta:
        verbose_name = "Предмет"
        verbose_name_plural = "Предмети"

    def __str__(self):
        return self.name

@register_snippet
class ClassGroup(models.Model):
    name = models.CharField("Клас", max_length=20)  # e.g. 10-A (ОЧНЕ)
    study_type = models.CharField("Тип навчання", max_length=20, default="ОЧНЕ", 
                                   choices=[("ОЧНЕ", "Очне"), ("ДИСТ.", "Дистанційне")])

    class Meta:
        verbose_name = "Клас"
        verbose_name_plural = "Класи"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.study_type})"

class Day(models.IntegerChoices):
    MONDAY = 1, 'Понеділок'
    TUESDAY = 2, 'Вівторок'
    WEDNESDAY = 3, 'Середа'
    THURSDAY = 4, 'Четвер'
    FRIDAY = 5, "П'ятниця"

class Week(models.IntegerChoices):
    WEEK_1 = 1, 'I тиждень'
    WEEK_2 = 2, 'II тиждень'
    WEEK_3 = 3, 'III тиждень'
    WEEK_4 = 4, 'IV тиждень'

# Lesson time slots
LESSON_TIMES = {
    1: "08:55 – 09:45",
    2: "09:50 – 10:35",
    3: "10:45 – 11:30",
    4: "11:35 – 12:20",
    5: "12:40 – 13:25",
    6: "13:30 – 14:15",
    7: "14:25 – 15:10",
    8: "15:15 – 16:00",
}

class Lesson(models.Model):
    class_group = models.ForeignKey(ClassGroup, on_delete=models.CASCADE, verbose_name="Клас")
    day = models.IntegerField(choices=Day.choices, verbose_name="День тижня")
    para_number = models.IntegerField("Номер пари", default=1, choices=[(1, "I пара"), (2, "II пара"), (3, "III пара"), (4, "IV пара")])
    para_part = models.IntegerField("Частина пари", default=0, choices=[(0, "Повна пара"), (1, "1-ша половина"), (2, "2-га половина")])
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name="Предмет")
    cabinet = models.CharField("Кабінет", max_length=20, blank=True, default="")
    week = models.IntegerField(choices=Week.choices, default=1, verbose_name="Тиждень (I-IV)")
    sub_group = models.IntegerField("Підгрупа", default=0, choices=[(0, "Весь клас"), (1, "1 підгрупа"), (2, "2 підгрупа")])

    panels = [
        FieldPanel('class_group'),
        FieldPanel('week'),
        FieldPanel('day'),
        FieldPanel('para_number'),
        FieldPanel('para_part'),
        FieldPanel('subject'),
        FieldPanel('cabinet'),
        FieldPanel('sub_group'),
    ]

    class Meta:
        ordering = ['week', 'day', 'para_number', 'para_part', 'class_group']
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"

    def __str__(self):
        part_display = self.get_para_part_display()
        return f"{self.class_group} - {self.get_day_display()} - {self.get_para_number_display()} ({part_display}) - {self.subject}"
    
    @property
    def time(self):
        if self.para_part == 0: # Full
            start = LESSON_TIMES.get(self.para_number * 2 - 1).split(' – ')[0]
            end = LESSON_TIMES.get(self.para_number * 2).split(' – ')[1]
            return f"{start} – {end}"
        elif self.para_part == 1: # 1st half
            return LESSON_TIMES.get(self.para_number * 2 - 1, "")
        else: # 2nd half
            return LESSON_TIMES.get(self.para_number * 2, "")

class LessonViewSet(SnippetViewSet):
    model = Lesson
    icon = "table"
    list_display = ("week", "day", "para_number", "class_group", "subject", "cabinet")
    list_filter = ("week", "day", "class_group")
    search_fields = ("subject__name", "cabinet")

register_snippet(LessonViewSet)


@register_setting
class ScheduleSettings(BaseSiteSetting):
    academic_year_structure_doc = models.ForeignKey(
        "wagtaildocs.Document",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Структура навчального року",
        help_text="Документ зі структурою навчального року (PDF/DOCX тощо)",
    )
    academic_year_structure_title = models.CharField(
        "Назва (Структура навчального року)",
        max_length=255,
        blank=True,
        default="Структура навчального року",
        help_text="Необов'язково. За замовчуванням: 'Структура навчального року'",
    )
    semester_weeks_doc = models.ForeignKey(
        "wagtaildocs.Document",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Тижні семестру навчального року",
        help_text="Документ з тижнями семестру навчального року (PDF/DOCX тощо)",
    )
    semester_weeks_title = models.CharField(
        "Назва (Тижні семестру)",
        max_length=255,
        blank=True,
        default="Тижні семестру навчального року",
        help_text="Необов'язково. За замовчуванням: 'Тижні семестру навчального року'",
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("academic_year_structure_title"),
                FieldPanel("academic_year_structure_doc"),
            ],
            heading="Структура навчального року",
        ),
        MultiFieldPanel(
            [
                FieldPanel("semester_weeks_title"),
                FieldPanel("semester_weeks_doc"),
            ],
            heading="Тижні семестру навчального року",
        ),
    ]

    class Meta:
        verbose_name = "Налаштування розкладу та документи"
        verbose_name_plural = "Налаштування розкладу та документи"

    def __str__(self):
        return "Налаштування розкладу та документи"

