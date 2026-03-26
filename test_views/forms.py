from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, HTML, Field, Div

COLOR_CHOICES = (
    ('red', 'Red'),
    ('green', 'Green'),
    ('blue', 'Blue')
)


class MultipleFileInput(forms.FileInput):
    def __init__(self, attrs=None):
        super().__init__(attrs)
        self.attrs.update({'multiple': True})

    def value_from_datadict(self, data, files, name):
        if files and hasattr(files, 'getlist'):
            return files.getlist(name)
        return super().value_from_datadict(data, files, name)

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result
    
        
class FormExample(forms.Form):
    text            = forms.CharField(label="Nom complet")
    email           = forms.EmailField(label="Adresse Email")
    number          = forms.CharField(label="Âge", widget=forms.NumberInput())
    url             = forms.CharField(label="Site Web", widget=forms.URLInput())
    password        = forms.CharField(label="Mot de passe", widget=forms.PasswordInput())
    select          = forms.ChoiceField(label="Couleur unique", choices=COLOR_CHOICES)
    multi_select    = forms.MultipleChoiceField(label="Couleurs multiples", choices=COLOR_CHOICES)
    textarea        = forms.CharField(label="Message", widget=forms.Textarea())
    checkbox        = forms.BooleanField(label="J'accepte les conditions", required=True)
    checkboxes      = forms.MultipleChoiceField(
                        label="Options à cocher",
                        choices=COLOR_CHOICES,
                        widget=forms.CheckboxSelectMultiple()
                    )
    radios          = forms.ChoiceField(
                        label="Choix exclusif",
                        choices=COLOR_CHOICES,
                        widget=forms.RadioSelect()
                    )
    file = MultipleFileField(
        label="Documents justificatifs",
        required=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        
        self.helper.layout = Layout(
            Fieldset(
                '👤 Informations personnelles',
                Div(
                    Div(Field('text', placeholder="Ex: Jean Dupont", icon_left="fas fa-user"), css_class='column is-6'),
                    Div(Field('email', placeholder="jean@email.com", icon_left="fas fa-envelope"), css_class='column is-6'),
                    css_class='columns' 
                ),
                Div(
                    Div(Field('password', icon_left="fas fa-lock"), css_class='column is-6'),
                    Div(Field('number', icon_left="fas fa-hashtag"), css_class='column is-6'),
                    css_class='columns'
                )
            ),

            HTML('<hr class="my-5">'),

            Fieldset(
                '🎨 Préférences visuelles',
                Div(
                    Div('select', css_class='column is-4'),
                    Div('multi_select', css_class='column is-4'),
                    Div(Field('url', placeholder="https://...", icon_left="fas fa-link"), css_class='column is-4'),
                    css_class='columns'
                ),
                'textarea',
            ),

            HTML('<hr class="my-5">'),

            Fieldset(
                '🔘 Choix et Fichiers',
                Div(
                    Div('checkboxes', css_class='column is-4'),
                    Div('radios', css_class='column is-4'),
                    Div(Field('file', template="elixir_toolkit/components/fields/file_input.html"), css_class='column is-4'),
                    css_class='columns'
                ),
                'checkbox',
            ),

            HTML("""
                <div class="field mt-5">
                    <div class="control">
                        <button type="submit" class="button is-primary is-fullwidth">
                            <span class="icon"><i class="fas fa-paper-plane"></i></span>
                            <span>Envoyer le formulaire</span>
                        </button>
                    </div>
                </div>
            """)
        )