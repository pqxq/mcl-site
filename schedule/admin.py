from django.contrib import admin
from .models import ClassGroup, Lesson, ScheduleSettings, Subject


@admin.register(ScheduleSettings)
class ScheduleSettingsAdmin(admin.ModelAdmin):
    list_display = ("__str__", "academic_year_structure_doc", "semester_weeks_doc")


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(ClassGroup)
class ClassGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "study_type")
    list_filter = ("study_type",)
    search_fields = ("name",)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("week", "day", "para_number", "para_part", "class_group", "subject", "cabinet", "sub_group")
    list_filter = ("week", "day", "class_group", "para_number")
    search_fields = ("subject__name", "cabinet", "class_group__name")

