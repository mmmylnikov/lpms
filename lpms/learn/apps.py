from django.apps import AppConfig


class LearnConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'learn'
    verbose_name = 'Обучение'

    def ready(self) -> None:
        import learn.signals  # noqa
        return super().ready()
