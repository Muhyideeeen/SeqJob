from django.apps import AppConfig


class MedicalsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'medicals'


    def ready(self) -> None:
        from . import signals