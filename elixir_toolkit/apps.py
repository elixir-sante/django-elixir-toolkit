from django.apps import AppConfig
from django.conf import settings

from . import defaults


def _inject_defaults():
    for name in dir(defaults):
        if name.isupper() and not name.startswith('_'):
            if not hasattr(settings, name):
                setattr(settings, name, getattr(defaults, name))


_inject_defaults()


def _patch_date_input():
    """Rend `forms.DateInput` natif, pour que le `DateField` standard de Django
    suffise : aucun widget ni champ spécifique à retenir côté formulaire.

    - `input_type = "date"` : input HTML5 natif.
    - format de la valeur forcé en ISO, imposé par la spec HTML pour l'attribut
      `value` d'un `input[type="date"]`. Un `format=` explicite reste prioritaire.

    `DateTimeInput` et `TimeInput` sont des classes sœurs de `DateInput`
    (parent commun `DateTimeBaseInput`) : elles ne sont pas touchées.

    Le placeholder grisé et la croix de réinitialisation sont assurés par
    `elixir_toolkit/js/date-input.js` et `elixir_toolkit/css/date-input.css`,
    chargés par `{% toolkit_assets %}`.
    """
    from django import forms

    if getattr(forms.DateInput, "_elixir_patched", False):
        return

    django_init = forms.DateInput.__init__

    def __init__(self, attrs=None, format=None):
        django_init(self, attrs, format or "%Y-%m-%d")

    forms.DateInput.__init__ = __init__
    forms.DateInput.input_type = "date"
    forms.DateInput._elixir_patched = True


class ElixirToolkitConfig(AppConfig):
    name = 'elixir_toolkit'

    def ready(self):
        _patch_date_input()
