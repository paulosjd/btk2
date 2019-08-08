from django.apps import AppConfig as AppCfg


class AppConfig(AppCfg):
    name = 'app'

    def ready(self):
        import app.signals
