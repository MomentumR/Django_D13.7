from django.apps import AppConfig


class PcfConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pcf'

    def ready(self):
        import pcf.signals