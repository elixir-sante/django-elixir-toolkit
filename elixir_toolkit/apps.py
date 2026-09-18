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


def _patch_char_field():
    """Branche la limite de caractères du toolkit sur le `max_length` standard
    de `forms.CharField` : `CKEditor5Field(max_length=400)` sur le modèle ou
    `forms.CharField(max_length=400)` dans le formulaire suffit.

    - `data-max-length` sur le widget : `elixir_toolkit/js/max-length.js` bloque
      la frappe et le collage au-delà de la limite et affiche un compteur ;
      pas de `maxlength` natif sur CKEditor (textarea masqué, contenu HTML).
    - le `MaxLengthValidator` de Django est remplacé à la validation par
      `RichTextMaxLengthValidator` (CKEditor, texte visible) ou
      `TextMaxLengthValidator` (retour à la ligne = 1 caractère, comme le
      navigateur). Le choix se fait sur le widget courant : un widget remplacé
      après l'init reste bien validé.
    """
    from django import forms
    from django.core.exceptions import ValidationError
    from django.core.validators import MaxLengthValidator

    from .forms import is_rich_text_widget
    from .validators import RichTextMaxLengthValidator, TextMaxLengthValidator

    if getattr(forms.CharField, "_elixir_patched", False):
        return

    django_init = forms.CharField.__init__
    django_widget_attrs = forms.CharField.widget_attrs
    django_run_validators = forms.CharField.run_validators

    def __init__(self, *args, **kwargs):
        django_init(self, *args, **kwargs)
        if self.max_length is None:
            return
        # Retire le MaxLengthValidator ajouté par Django, pas ceux passés en `validators=`
        for validator in reversed(self.validators):
            if type(validator) is MaxLengthValidator and validator.limit_value == int(self.max_length):
                self.validators.remove(validator)
                break

    def widget_attrs(self, widget):
        attrs = django_widget_attrs(self, widget)
        if self.max_length is not None and not widget.is_hidden:
            attrs["data-max-length"] = str(self.max_length)
            if is_rich_text_widget(widget):
                attrs.pop("maxlength", None)
        return attrs

    def run_validators(self, value):
        errors = []
        try:
            django_run_validators(self, value)
        except ValidationError as e:
            errors.extend(e.error_list)

        if self.max_length is not None and value not in self.empty_values:
            validator_class = RichTextMaxLengthValidator if is_rich_text_widget(self.widget) else TextMaxLengthValidator
            try:
                validator_class(int(self.max_length))(value)
            except ValidationError as e:
                if e.code in self.error_messages:
                    e.message = self.error_messages[e.code]
                errors.extend(e.error_list)

        if errors:
            raise ValidationError(errors)

    forms.CharField.__init__ = __init__
    forms.CharField.widget_attrs = widget_attrs
    forms.CharField.run_validators = run_validators
    forms.CharField._elixir_patched = True


class ElixirToolkitConfig(AppConfig):
    name = 'elixir_toolkit'

    def ready(self):
        _patch_date_input()
        _patch_char_field()
