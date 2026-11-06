import json

from crispy_forms.layout import Field as CrispyField
from crispy_forms.helper import FormHelper
from django import forms
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe

from elixir_toolkit.validators import (
    MaxFileSizeValidator,
    MaxTotalSizeValidator,
    AllowedExtensionsValidator,
    MaxFilesValidator,
    IBANValidator,
    IBAN_MAX_LENGTH,
    normalize_iban,
)

def is_rich_text_widget(widget):
    """Widget CKEditor : classe posée par CKEditor5Widget, évite d'importer django_ckeditor_5."""
    return "django_ckeditor_5" in widget.attrs.get("class", "").split()


def format_file_size(size):
    """Formate une taille en octets pour l'affichage (Mo / Ko / octets)."""
    if size >= 1024 * 1024:
        value = size / (1024 * 1024)
        return f"{int(value)} Mo" if value.is_integer() else f"{value:.1f}".replace(".", ",") + " Mo"
    if size >= 1024:
        value = size / 1024
        return f"{int(value)} Ko" if value.is_integer() else f"{value:.1f}".replace(".", ",") + " Ko"
    return f"{size} octet" if size == 1 else f"{size} octets"


def generate_file_help_text(max_size, allowed_extensions, max_files=None, max_total_size=None):
    """Construit le help_text par défaut des champs d'upload à partir de
    leurs propriétés : nombre de fichiers, taille maximale et formats acceptés.

    Écrasé totalement si `help_text` est passé au champ.
    """
    parts = []
    if max_files is not None:
        parts.append(f"{max_files} fichier{'s' if max_files > 1 else ''} maximum")
    if max_total_size is not None:
        parts.append(
            f"{format_file_size(max_size)} maximum par fichier "
            f"({format_file_size(max_total_size)} au total)"
        )
    else:
        parts.append(f"{format_file_size(max_size)} maximum")
    extensions = ", ".join(ext.upper() for ext in allowed_extensions)
    parts.append(f"formats acceptés : {extensions}")
    sentence = ". ".join(part[:1].upper() + part[1:] for part in parts)
    return sentence + "."


def limit_length(field, max_length):
    """Change après coup le `max_length` d'un `forms.CharField` (limite dynamique).

    Pour une limite fixe, passer directement `max_length` au champ (cf. `apps._patch_char_field`).
    """
    field.max_length = max_length
    field.widget.attrs.pop("maxlength", None)
    field.widget.attrs.update(field.widget_attrs(field.widget))


# Les scripts des helpers s'exécutent au rendu du formulaire, qu'il soit dans
# la page initiale ou injecté par HTMX (balises <script> exécutées au swap) :
# `DOMContentLoaded` seul ne suffit pas, il est déjà passé pour un formulaire
# chargé par HTMX. Ils ne visent que le <form> qui les contient
# (`document.currentScript`), et chaque élément n'est branché qu'une fois.
FORM_VALIDATOR_SCRIPT = """
<script>
(function (script) {
    function init() {
        var form = script && script.closest('form');
        var root = form || document;
        root.querySelectorAll('input, textarea, select').forEach(function (input) {
            if (input.dataset.toolkitValidator) { return; }
            input.dataset.toolkitValidator = 'true';
            var validate = function () {
                input.classList.toggle('input-error', !input.checkValidity());
            };
            input.addEventListener('input', validate);
            input.addEventListener('blur', validate);
        });
    }
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})(document.currentScript);
</script>
"""

SUBMIT_BUTTON_LOADING_SCRIPT = """
<script>
(function (script) {
    var SUBMIT_SELECTOR = 'button[type="submit"], input[type="submit"]';

    function stopLoading(root) {
        root.querySelectorAll(SUBMIT_SELECTOR).forEach(function (button) {
            button.classList.remove('is-loading');
        });
    }

    function bind(form) {
        if (form.dataset.toolkitSubmitLoading) { return; }
        form.dataset.toolkitSubmitLoading = 'true';
        form.addEventListener('submit', function (e) {
            var submitButton = e.submitter || form.querySelector(SUBMIT_SELECTOR);
            if (submitButton) {
                // Bulma `is-loading` : spinner + clics bloqués, pas de double envoi.
                submitButton.classList.add('is-loading');
            }
        });
        // Formulaire HTMX : réponse sans redirection (erreur, formulaire non
        // remplacé…) → bouton réactivé. Avec redirection, il reste en loading.
        form.addEventListener('htmx:afterRequest', function (e) {
            if (e.detail.elt !== form) { return; }
            var xhr = e.detail.xhr;
            var redirects = xhr && (xhr.getResponseHeader('HX-Redirect') || xhr.getResponseHeader('HX-Location') || xhr.getResponseHeader('HX-Refresh'));
            if (!e.detail.successful || !redirects) {
                stopLoading(form);
            }
        });
    }

    function init() {
        var form = script && script.closest('form');
        (form ? [form] : document.querySelectorAll('form')).forEach(bind);
    }

    // Retour arrière (bfcache) : la page revient telle quelle, bouton compris.
    if (!window.toolkitSubmitLoadingPageshow) {
        window.toolkitSubmitLoadingPageshow = true;
        window.addEventListener('pageshow', function (e) {
            if (e.persisted) { stopLoading(document); }
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})(document.currentScript);
</script>
"""


class SuperFormHelper(FormHelper):
    """`FormHelper` crispy avec deux comportements optionnels :

    - `enable_form_validator` : classe `input-error` sur un champ invalide (saisie / sortie) ;
    - `enable_submit_button_loading` : `is-loading` sur le bouton au submit (anti double envoi).

    Fonctionne pour un formulaire de la page comme pour un formulaire chargé par HTMX.
    Le layout n'est pas modifié : les scripts sont ajoutés au rendu.
    """

    enable_form_validator = False
    enable_submit_button_loading = False

    def render_layout(self, form, context, template_pack=None):
        html = super().render_layout(form, context, template_pack)
        if not self.layout:
            return html
        if self.enable_form_validator:
            html += mark_safe(FORM_VALIDATOR_SCRIPT)
        if self.enable_submit_button_loading:
            html += mark_safe(SUBMIT_BUTTON_LOADING_SCRIPT)
        return html


class CustomFormHelper:
    """Mixin de formulaire : fournit un `helper` prêt à l'emploi.

    À hériter avec `forms.Form` (ce n'est pas un `FormHelper`) :

        class MyForm(CustomFormHelper, forms.Form):
            layout = Layout(...)   # attribut ou propriété, optionnel

    Le helper est un `SuperFormHelper` avec `form_tag = False` (balise <form> à
    écrire dans le template), validation visuelle et loading du bouton activés,
    et le `layout` du formulaire s'il en définit un. Pour le personnaliser,
    affecter un autre helper (`self.helper = ...`) : il est alors utilisé tel quel.
    """

    @property
    def helper(self):
        custom_helper = getattr(self, "_custom_helper", None)
        if custom_helper is not None:
            return custom_helper
        helper = SuperFormHelper()
        helper.form_tag = False
        helper.enable_form_validator = True
        helper.enable_submit_button_loading = True
        if hasattr(self, "layout"):
            helper.layout = self.layout
        return helper

    @helper.setter
    def helper(self, value):
        self._custom_helper = value


class MultipleFileUploadInput(forms.FileInput):
    """`FileInput` multiple, sans le bloc « Actuellement / Effacer » du Clearable."""
    allow_multiple_selected = True


class SingleFileInput(forms.FileInput):
    """`FileInput` qui renvoie la liste si plusieurs fichiers sont envoyés,
    au lieu de garder silencieusement le dernier (cf. `ToolkitFileField.clean`)."""

    def value_from_datadict(self, data, files, name):
        uploaded = files.getlist(name) if hasattr(files, "getlist") else []
        if len(uploaded) > 1:
            return uploaded
        return super().value_from_datadict(data, files, name)


class SingleClearableFileInput(SingleFileInput, forms.ClearableFileInput):
    """Variante « clearable » de `SingleFileInput`."""


class FileUpload(CrispyField):
    def __init__(self, *args, **kwargs):
        kwargs['template'] = "elixir_toolkit/components/fields/file_input.html"
        super().__init__(*args, **kwargs)

    def render(self, form, context, template_pack=None, **kwargs):
        # On récupère le champ Django associé
        bound_field = form[self.fields[0]]
        current_widget = bound_field.field.widget
        # Un `FileInput` simple refuse l'attribut `multiple` (ValueError depuis
        # Django 4.2.1) : les champs multiples gardent un widget multiple.
        widget_class = (
            MultipleFileUploadInput
            if current_widget.allow_multiple_selected
            else SingleFileInput
        )
        bound_field.field.widget = widget_class(attrs=current_widget.attrs)

        return super().render(form, context, template_pack, **kwargs)


class ToolkitFileField(forms.FileField):
    def __init__(
        self,
        max_size=5 * 1024 * 1024,
        allowed_extensions=None,
        *args,
        **kwargs
    ):
        self.max_size = max_size
        self.allowed_extensions = allowed_extensions or ['pdf', 'png', 'jpg', 'jpeg']

        # help_text par défaut déduit des limites, écrasé si transmis explicitement
        kwargs.setdefault('help_text', generate_file_help_text(
            self.max_size,
            self.allowed_extensions,
        ))

        # Injection des validateurs unitaires pour fichier unique
        kwargs.setdefault('validators', [])
        kwargs['validators'].extend([
            MaxFileSizeValidator(self.max_size),
            AllowedExtensionsValidator(self.allowed_extensions),
        ])

        # Widget mono-fichier dès l'instanciation : au POST, le formulaire est
        # recréé sans passer par `FileUpload.render`, et un widget standard
        # garderait silencieusement le dernier fichier au lieu de lever l'erreur.
        widget = kwargs.get('widget') or self.widget
        if isinstance(widget, type):
            widget = widget()
        if not widget.allow_multiple_selected:
            single_class = (
                SingleClearableFileInput
                if isinstance(widget, forms.ClearableFileInput)
                else SingleFileInput
            )
            kwargs['widget'] = single_class(attrs=widget.attrs)

        super().__init__(*args, **kwargs)

    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        attrs.update({
            'data-max-size': self.max_size,
            # Fichier unique : la taille totale vaut la taille unitaire
            # (sinon le JS de file_input.html retombe sur 5 Mo)
            'data-max-total-size': self.max_size,
            'data-allowed-extensions': json.dumps(self.allowed_extensions),
            'data-max-files': 1,
            'accept': ",".join(f".{e}" for e in self.allowed_extensions),
        })
        return attrs

    def clean(self, data, initial=None):
        if isinstance(data, (list, tuple)):
            raise ValidationError("Vous ne pouvez joindre qu'un seul fichier.", code='too_many_files')
        return super().clean(data, initial)


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(
        self,
        max_size=5 * 1024 * 1024,
        max_total_size=5 * 1024 * 1024,
        allowed_extensions=None,
        max_files=5,
        *args,
        **kwargs
    ):
        self.max_size = max_size
        self.max_total_size = max_total_size
        self.allowed_extensions = allowed_extensions or ['pdf', 'png', 'jpg', 'jpeg']
        self.max_files = max_files

        # help_text par défaut déduit des limites, écrasé si transmis explicitement
        kwargs.setdefault('help_text', generate_file_help_text(
            self.max_size,
            self.allowed_extensions,
            max_files=self.max_files,
            max_total_size=self.max_total_size,
        ))

        # Validateurs appliqués fichier par fichier, dans le clean() splitté
        kwargs.setdefault('validators', [])
        kwargs['validators'].extend([
            MaxFileSizeValidator(self.max_size),
            AllowedExtensionsValidator(self.allowed_extensions),
        ])
        # Validateurs qui doivent voir la liste complète
        self._batch_validators = [
            MaxTotalSizeValidator(self.max_total_size),
            MaxFilesValidator(self.max_files),
        ]

        kwargs.setdefault('widget', MultipleFileInput())
        super().__init__(*args, **kwargs)

    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        attrs.update({
            'data-max-size': self.max_size,
            'data-max-total-size': self.max_total_size,
            'data-allowed-extensions': json.dumps(self.allowed_extensions),
            'data-max-files': self.max_files,
            'accept': ",".join(f".{e}" for e in self.allowed_extensions),
        })
        return attrs

    def clean(self, data, initial=None):
        single_file_clean = super().clean

        if isinstance(data, (list, tuple)):
            cleaned = [single_file_clean(d, initial) for d in data]
            self._run_batch_validators(cleaned)
            return cleaned

        if not data:
            return single_file_clean(data, initial)

        cleaned = [single_file_clean(data, initial)]
        self._run_batch_validators(cleaned)
        return cleaned[0]

    def _run_batch_validators(self, cleaned_files):
        if not cleaned_files:
            return
        for validator in self._batch_validators:
            validator(cleaned_files)


# Grille Bulma standard pour les Layouts crispy : utiliser ces constantes avec
# des Div, ne jamais écrire les classes CSS à la main dans les formulaires.
#
#     Layout(
#         Div(
#             Div('champ1', css_class=COLUMN_HALF_CLASS),
#             Div('champ2', css_class=COLUMN_HALF_CLASS),
#             css_class=ROW_CLASS,
#         ),
#     )

ROW_CLASS = "columns is-multiline"

COLUMN_THIRD_CLASS = "column is-6-tablet is-4-desktop"

COLUMN_HALF_CLASS = "column is-12-mobile is-6-tablet"

COLUMN_QUARTER_CLASS = "column is-12-mobile is-3-tablet"

COLUMN_FULL_CLASS = "column"


class IBANField(forms.CharField):
    """Champ IBAN : espaces de présentation acceptés, compteur de saisie.

    - valeur normalisée (espaces et tirets retirés, majuscules) avant validation ;
    - `IBANValidator` par défaut (remplaçable via `validators=`, ex. `FrenchIBANValidator`) ;
    - limite de 34 caractères (maximum de la norme) comptée hors espaces : compteur
      « n / 34 caractères » sous le champ (`max-length.js`), sans `maxlength` natif
      qui compterait les espaces.
    """

    default_validators = [IBANValidator()]

    def __init__(self, *, max_length=IBAN_MAX_LENGTH, **kwargs):
        super().__init__(max_length=max_length, **kwargs)

    def to_python(self, value):
        value = super().to_python(value)
        return normalize_iban(value) if value else value

    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        if self.max_length is not None and not widget.is_hidden:
            attrs.pop("maxlength", None)
            attrs["data-max-length-counter"] = True
            attrs["data-max-length-ignore-spaces"] = True
        return attrs


class PasswordWithIconField(CrispyField):
    template = "elixir_toolkit/components/fields/password_input.html"


class ToolkitSelectField(CrispyField):
    template = "elixir_toolkit/components/select.html"

    def __init__(self, *args, **kwargs):
        self.icon = kwargs.pop('icon', None)
        self.css_classes = kwargs.pop('css_classes', '')
        super().__init__(*args, **kwargs)

    def render(self, form, context, template_pack=None, **kwargs):
        bound_field = form[self.fields[0]]
        
        # Détection automatique du mode multiple basé sur le type de champ Django
        is_multiple = isinstance(bound_field.field, (forms.MultipleChoiceField, forms.ModelMultipleChoiceField))
        
        placeholder = getattr(bound_field.field, 'empty_label', None) or "Sélectionnez une option..."

        # Traitement de la valeur sélectionnée
        val = bound_field.value()
        if is_multiple:
            if hasattr(val, '__iter__') and not isinstance(val, (str, dict)):
                selected_list = [str(item.id) if hasattr(item, 'id') else str(item) for item in val]
            elif val:
                selected_list = [str(val)]
            else:
                selected_list = []
            selected_val = None
        else:
            selected_list = []
            selected_val = str(val) if val is not None else None

        custom_context = {
            'field': bound_field,
            'label': bound_field.label,
            'name': bound_field.html_name,
            'element_id': bound_field.auto_id,
            'options': bound_field.field.choices,
            'selected': selected_val,
            'selected_list': selected_list,
            'placeholder': placeholder,
            'icon': self.icon,
            'css_classes': self.css_classes,
            'multiple': is_multiple,
        }
        
        context.update(custom_context)
        return super().render(form, context, template_pack, **kwargs)