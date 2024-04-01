from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group as BaseGroup
from import_export.admin import ImportExportModelAdmin

from user.models import User, Group


class UserAdmin(ImportExportModelAdmin, BaseUserAdmin):
    fieldsets = (
        ('Персона', {'fields': (
            'first_name', 'last_name',
            )}),
        ('Учетная запись', {'fields': (
            'username', 'gh_username', 'tg_username', 'email',
            )}),
        ('Безопасность', {'fields': (
            'password',
            )}),
        ('Доступы', {'fields': (
            'is_active', 'is_staff', 'is_superuser', 'groups',
            )}),
      )


class GroupAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    pass


admin.site.unregister(BaseGroup)
admin.site.register(User, UserAdmin)
admin.site.register(Group, GroupAdmin)
