from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from learn.models import (Lesson, Challenge, Week, Program,
                          Homework, HomeworkStatus)


class AddedFieldAdminMixin:
    def added(self, object: Lesson | Challenge | Week | Program) -> str:
        return object.added
    added.short_description = 'Материалы'  # type: ignore
    """
    for ("# type: ignore"): I don't know how to resolve it:
    ----------------------------------------------------------------
    mypy: learn/admin.py:10: error: "Callable[[AddedFieldAdminMixin,
    Lesson | Challenge | Week | Program], str]" has no attribute
    "short_description"  [attr-defined]
    ----------------------------------------------------------------
    """


class LessonAdmin(AddedFieldAdminMixin, ImportExportModelAdmin,
                  admin.ModelAdmin):
    list_display = ('track', 'order', 'name', 'added', )
    list_display_links = ('name',)
    list_editable = ('order', )
    list_filter = ('track', 'track__course', )
    ordering = ('track', 'order', 'name')


class ChallengeAdmin(AddedFieldAdminMixin, ImportExportModelAdmin,
                     admin.ModelAdmin):
    list_display = ('track', 'order', 'name', 'added')
    list_display_links = ('name',)
    list_editable = ('order', )
    list_filter = ('track', 'track__course', )
    ordering = ('track', 'order', 'name')


class HomeworkAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('updated_at', 'challenge', 'user')
    list_display_links = ('user',)
    list_filter = ('challenge__track', 'user', 'team', 'updated_at',)
    ordering = ('challenge', 'user')


class HomeworkStatusAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('updated_at',  'tutor', 'student', 'status', 'homework', )
    list_display_links = ('homework',)
    list_filter = ('homework__challenge__track', 'student', 'tutor', 'status',
                   'updated_at')
    ordering = ('tutor',  'student', 'updated_at', )


class WeekAdmin(AddedFieldAdminMixin, ImportExportModelAdmin,
                admin.ModelAdmin):
    list_display = ('course', 'number', 'added')
    list_display_links = ('number',)
    list_filter = ('course', )
    filter_horizontal = ('lessons', 'challenges')
    ordering = ('course', 'number')


class ProgramAdmin(AddedFieldAdminMixin, ImportExportModelAdmin,
                   admin.ModelAdmin):
    list_display = ('course', 'name', 'added')
    list_display_links = ('name',)
    list_filter = ('course', )
    filter_horizontal = ('weeks', 'enrollments')
    ordering = ('course', 'name')


admin.site.register(Lesson, LessonAdmin)
admin.site.register(Challenge, ChallengeAdmin)
admin.site.register(Homework, HomeworkAdmin)
admin.site.register(HomeworkStatus, HomeworkStatusAdmin)

admin.site.register(Week, WeekAdmin)
admin.site.register(Program, ProgramAdmin)
