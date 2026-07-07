from django.apps import AppConfig
from django.conf import settings

from . import defaults


def _inject_defaults():
    for name in dir(defaults):
        if name.isupper() and not name.startswith('_'):
            if not hasattr(settings, name):
                setattr(settings, name, getattr(defaults, name))


_inject_defaults()


class ElixirToolkitConfig(AppConfig):
    name = 'elixir_toolkit'
