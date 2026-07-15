from crispy_forms.layout import Field as CrispyField
from crispy_forms.helper import FormHelper
from django import forms


class CustomFormHelper:
    
    @property
    def helper(self):
        if not hasattr(self, '_helper'):
            self._helper = FormHelper()
            self._helper.form_tag = False
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
