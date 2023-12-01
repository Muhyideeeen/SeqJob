from django.apps import AppConfig


class MyauthenticationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myauthentication'

    def ready(self) -> None:
        from . import signals