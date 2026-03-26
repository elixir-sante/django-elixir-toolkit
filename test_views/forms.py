from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, HTML, Field, Div

COLOR_CHOICES = (
    ('red', 'Red'), ('green', 'Green'), ('blue', 'Blue')
)

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
    file = MultipleFileField(label="Documents justificatifs", required=True)
    file2 = forms.FileField(label="Documents test", required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        # IMPORTANT: S'assurer que le template pack est bien défini ici si besoin
        self.helper.template_pack = 'bulma' 
        
        self.helper.layout = Layout(
            Fieldset(
                '👤 Informations personnelles',
                Div(
                    Div(Field('text', placeholder="Ex: Jean Dupont"), css_class='column is-6'),
                    Div(Field('email', placeholder="jean@email.com"), css_class='column is-6'),
                    css_class='columns' 
                ),
                Div(
                    Div(Field('password'), css_class='column is-6'),
                    Div(Field('number'), css_class='column is-6'),
                    css_class='columns'
                )
            ),
            HTML('<hr class="my-5">'),
            Fieldset(
                '🎨 Préférences visuelles',
                Div(
                    Div('select', css_class='column is-4'),
                    Div('multi_select', css_class='column is-4'),
                    Div(Field('url'), css_class='column is-4'),
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
                    # On repasse en mode explicite pour éviter le bug de détection
                    Div(Field('file', template="elixir_toolkit/components/fields/file_input.html"), css_class='column is-4'),
                    css_class='columns'
                ),
                Div(Div(Field('file2', template="elixir_toolkit/components/fields/file_input.html"), css_class='column is-4'),),
                'checkbox',
            ),
            HTML("""
                <div class="field mt-5"><div class="control">
                    <button type="submit" class="button is-primary is-fullwidth">
                        <span class="icon"><i class="fas fa-paper-plane"></i></span>
                        <span>Envoyer le formulaire</span>
                    </button>
                </div></div>
            """)
        )