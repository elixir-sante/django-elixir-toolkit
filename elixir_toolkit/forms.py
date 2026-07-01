from crispy_forms.layout import Field
from crispy_forms.helper import FormHelper
from django import forms


class CustomFormHelper:
    @property
    def helper(self):
        helper = FormHelper()
        helper.form_tag = False
        return helper


class FileUpload(Field):
    def __init__(self, *args, **kwargs):
        kwargs['template'] = "elixir_toolkit/components/fields/file_input.html"
        super().__init__(*args, **kwargs)
        
        
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', MultipleFileInput())
        super().__init__(*args, **kwargs)
    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            return [single_file_clean(d, initial) for d in data]
        return [single_file_clean(data, initial)]

class ToolkitSelectField(Field):
    template = "elixir_toolkit/components/select.html"

    def __init__(self, *args, **kwargs):
        self.icon = kwargs.pop('icon', None)
        self.css_classes = kwargs.pop('css_classes', '')
        super().__init__(*args, **kwargs)

    def render(self, form, context, template_pack=None, **kwargs):
        bound_field = form[self.fields[0]]
        
        # 💡 Sécurisation ici : on cherche empty_label, sinon on met "Sélectionnez..."
        placeholder = getattr(bound_field.field, 'empty_label', None) or "Sélectionnez une option..."

        custom_context = {
            'field': bound_field,
            'name': bound_field.html_name,
            'element_id': bound_field.auto_id,
            'options': bound_field.field.choices,
            'selected': str(bound_field.value()) if bound_field.value() is not None else None,
            'placeholder': placeholder,  # Utilise la variable sécurisée
            'icon': self.icon,
            'css_classes': self.css_classes,
        }
        
        context.update(custom_context)
        return super().render(form, context, template_pack, **kwargs)
