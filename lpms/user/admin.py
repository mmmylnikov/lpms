from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group as BaseGroup
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin

from user.models import User, Repo, Pull


class UserAdmin(ImportExportModelAdmin, BaseUserAdmin):
    fieldsets = (
        ('Персона', {'fields': (
            'first_name', 'last_name',
            )}),
        ('Учетная запись', {'fields': (
            'username', 'gh_username', 'tg_username', 'email', 'notify',
            )}),
        ('Безопасность', {'fields': (
            'password',
            )}),
        ('Доступы', {'fields': (
            'is_active',
            'is_tutor', 'is_admin',
            'is_staff', 'is_superuser',
            )}),
      )
    list_display = (
        'username', 'full_name',
        'github_url', 'tg_url', 'email_url',
        'is_active', 'is_tutor', 'is_admin', 'is_staff', 'is_superuser',
        )
    list_display_links = ('username', 'full_name',)
    list_filter = (
        'is_tutor', 'is_admin', 'is_staff',
        'is_superuser', 'is_active',
        )
    search_fields = (
        'username', 'gh_username', 'tg_username', 'email',
        'first_name', 'last_name',
        )

    @admin.display(description="Github")
    def github_url(self, obj: User) -> str:
        if not obj.gh_username:
            return ''
        return format_html(
            "<a href='{url}'>{label}</a>",
            url=obj.github_url,
            label=obj.gh_username,
        )

    @admin.display(description="Telegram")
    def tg_url(self, obj: User) -> str:
        if not obj.tg_username:
            return ''
        return format_html(
            "<a href='{url}'>{label}</a>",
            url=obj.tg_url,
            label=obj.tg_username,
        )

    @admin.display(description="EMAIL")
    def email_url(self, obj: User) -> str:
        if not obj.email:
            return ''
        return format_html(
            "<a href='{url}'>{label}</a>",
            url=obj.email_url,
            label=obj.email,
        )


class RepoAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('user', 'full_name', )
    list_display_links = ('full_name', )


class PullAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('repo', 'number', 'title', )
    list_display_links = ('title', )


admin.site.unregister(BaseGroup)
admin.site.register(User, UserAdmin)
admin.site.register(Repo, RepoAdmin)
admin.site.register(Pull, PullAdmin)
