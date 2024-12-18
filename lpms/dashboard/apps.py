from django.apps import AppConfig

from health_check.plugins import plugin_dir


class DashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dashboard'

    def ready(self) -> None:
        from backends.health_check import StaticHealthCheck, MediaHealthCheck
        plugin_dir.register(StaticHealthCheck)
        plugin_dir.register(MediaHealthCheck)
