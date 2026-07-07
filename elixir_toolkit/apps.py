from django.apps import AppConfig
from django.conf import settings


class ElixirToolkitConfig(AppConfig):
    name = 'elixir_toolkit'

    def ready(self):
        from . import defaults
        for name in dir(defaults):
            if name.isupper() and not name.startswith('_'):
                if not hasattr(settings, name):
                    setattr(settings, name, getattr(defaults, name))
