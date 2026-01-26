from django.apps import AppConfig


class ApiLmsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api_lms'

    def ready(self):
        """Importar signals cuando la app esté lista"""
        import api_lms.signals  # ← AGREGAR ESTA LÍNEA
