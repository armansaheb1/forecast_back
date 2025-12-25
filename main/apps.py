from django.apps import AppConfig


class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'
    verbose_name = 'Main Application'

    def ready(self):
        """Called when Django starts"""
        # Import signal handlers if you add them later
        pass
