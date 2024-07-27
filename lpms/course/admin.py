from django.contrib import admin

from course.models import Course, Enrollment, Team, Track


class CourseAdmin(admin.ModelAdmin):
    pass


class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('slug', 'start', 'finish', 'is_completed', )
    list_filter = ('course', )


class TeamAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'tutor',)
    list_filter = ('tutor', 'enrollment', 'enrollment__course')
    filter_horizontal = ('students', )


class TrackAdmin(admin.ModelAdmin):
    list_display = ('course', 'name',)
    list_display_links = ('name',)
    list_filter = ('course', )
    ordering = ('course', 'created_at',)


admin.site.register(Course, CourseAdmin)
admin.site.register(Enrollment, EnrollmentAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Track, TrackAdmin)
