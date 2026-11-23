# app_prevenapp/apps.py
from django.apps import AppConfig

class AppPrevenappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_prevenapp'

    def ready(self):
        # Importamos las señales para que se registren al iniciar el servidor
        import app_prevenapp.signals