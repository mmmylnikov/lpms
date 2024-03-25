from django.contrib import admin

from learn.models import Lesson, Challenge, Homework, Week, Program


class LessonAdmin(admin.ModelAdmin):
    list_display = ('track', 'name', 'added')
    list_display_links = ('name',)
    list_filter = ('track', 'track__course', )
    ordering = ('track', 'created_at',)


class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('track', 'name', 'added')
    list_display_links = ('name',)
    list_filter = ('track', 'track__course', )
    ordering = ('track', 'created_at',)


class HomeworkAdmin(admin.ModelAdmin):
    list_display = ('updated_at', 'сhallenge', 'user')
    list_display_links = ('user',)
    list_filter = ('сhallenge__track', )
    ordering = ('сhallenge', 'user')


class WeekAdmin(admin.ModelAdmin):
    list_display = ('course', 'number', 'added')
    list_display_links = ('number',)
    list_filter = ('course', )
    filter_horizontal = ('lessons', 'challenges')
    ordering = ('course', 'number')


class ProgramAdmin(admin.ModelAdmin):
    list_display = ('course', 'name', 'added')
    list_display_links = ('name',)
    list_filter = ('course', )
    filter_horizontal = ('weeks', 'enrollments')
    ordering = ('course', 'name')


admin.site.register(Lesson, LessonAdmin)
admin.site.register(Challenge, ChallengeAdmin)
admin.site.register(Homework, HomeworkAdmin)
admin.site.register(Week, WeekAdmin)
admin.site.register(Program, ProgramAdmin)
