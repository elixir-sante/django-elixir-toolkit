import json

from crispy_forms.layout import Field as CrispyField
from crispy_forms.layout import HTML
from crispy_forms.helper import FormHelper
from django import forms

from elixir_toolkit.validators import (
    MaxFileSizeValidator,
    MaxTotalSizeValidator,
    AllowedExtensionsValidator,
    MaxFilesValidator,
)

class SuperFormHelper(FormHelper):
    
    enable_form_validator = False
    enable_submit_button_loading = False
    
    def render_layout(self, form, context, template_pack=None):

        # Ajout du script de validation au formulaire
        if self.layout and self.enable_form_validator:
            self.layout.append(HTML("""
            <script>
                document.addEventListener('DOMContentLoaded', function () {
                    document.querySelectorAll('input, textarea, select').forEach(function (input) {
                        var validate = function () {
                            input.classList.toggle('input-error', !input.checkValidity())
                        }
                        input.addEventListener('input', validate)
                        input.addEventListener('blur', validate)
                    })
                })
            </script>
            """))

        # Ajout de la propriété is-loading au bouton submit
        if self.layout and self.enable_submit_button_loading:
            self.layout.append(HTML("""
            <script>
                document.addEventListener('DOMContentLoaded', function () {
                    document.querySelectorAll('form').forEach(function (form) {
                        form.addEventListener('submit', function (e) {
                            var submitButton = e.submitter || form.querySelector('button[type="submit"]')
                            if (submitButton) {
                                submitButton.classList.add('is-loading')
                            }
                        })
                    })
                })
            </script>
            """))

        return super().render_layout(form, context, template_pack)


class CustomFormHelper:
    """CustomFormHelper :
     - ajoute automatiquement le JS de validation au formulaire
     - permet la personnalisation du helper via la surcharge de helper
    """
    
    @property
    def helper(self):
        self._helper = SuperFormHelper()
        self._helper.form_tag = False
        self._helper.enable_form_validator = True
        self._helper.enable_submit_button_loading = True
        if hasattr(self, 'layout'):
            self._helper.layout = self.layout
        return self._helper

    @helper.setter
    def helper(self, value):
        self._helper = value


class FileUpload(CrispyField):
    def __init__(self, *args, **kwargs):
        kwargs['template'] = "elixir_toolkit/components/fields/file_input.html"
        super().__init__(*args, **kwargs)

    def render(self, form, context, template_pack=None, **kwargs):
        # On récupère le champ Django associé
        bound_field = form[self.fields[0]]
        current_attrs = bound_field.field.widget.attrs
        bound_field.field.widget = forms.FileInput(attrs=current_attrs)

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

        # Injection des validateurs unitaires pour fichier unique
        kwargs.setdefault('validators', [])
        kwargs['validators'].extend([
            MaxFileSizeValidator(self.max_size),
            AllowedExtensionsValidator(self.allowed_extensions),
        ])

        super().__init__(*args, **kwargs)

    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        attrs.update({
            'data-max-size': self.max_size,
            'data-allowed-extensions': json.dumps(self.allowed_extensions),
        })
        return attrs


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

        # Injection automatique des 4 validateurs distincts
        kwargs.setdefault('validators', [])
        kwargs['validators'].extend([
            MaxFileSizeValidator(self.max_size),
            MaxTotalSizeValidator(self.max_total_size),
            AllowedExtensionsValidator(self.allowed_extensions),
            MaxFilesValidator(self.max_files),
        ])

        kwargs.setdefault('widget', MultipleFileInput())
        super().__init__(*args, **kwargs)

    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        attrs.update({
            'data-max-size': self.max_size,
            'data-max-total-size': self.max_total_size,
            'data-allowed-extensions': json.dumps(self.allowed_extensions),
            'data-max-files': self.max_files,
        })
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
