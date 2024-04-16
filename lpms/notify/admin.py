from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from notify.models import Provider, Account, Status, Message


class ProviderAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    pass


class AccountAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('user', 'provider', 'chat_uid')
    list_display_links = ('chat_uid', )
    list_filter = ('provider__name', )


class StatusAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('user', 'account', 'enabled', 'updated_at')
    list_display_links = ('user', )
    list_filter = ('updated_at', )


class MessageAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('user', 'account', 'status', 'text')
    list_display_links = ('text', )
    list_filter = ('status', )


admin.site.register(Provider, ProviderAdmin)
admin.site.register(Account, AccountAdmin)
admin.site.register(Status, StatusAdmin)
admin.site.register(Message, MessageAdmin)
