from django import forms
from crispy_forms.layout import Layout, Fieldset, HTML, Field, Div
from crispy_bulma.layout import IconField
from elixir_toolkit.forms import MultipleFileField, FileUpload, ToolkitSelectField, CustomFormHelper, PasswordWithIconField


COLOR_CHOICES = (
    ('red', 'Red'), ('green', 'Green'), ('blue', 'Blue')
)

class FormExample(CustomFormHelper, forms.Form):
    text            = forms.CharField(label="Nom complet")
    text_with_icon  = forms.CharField(label="Nom complet et icone")
    email           = forms.EmailField(label="Adresse Email")
    number          = forms.CharField(label="Âge", widget=forms.NumberInput())
    url             = forms.CharField(label="Site Web", widget=forms.URLInput())
    password        = forms.CharField(label="Mot de passe", widget=forms.PasswordInput(attrs={'placeholder': '********'}))
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
    
    @property
    def helper(self):
        helper = super().helper
        
        # IMPORTANT: S'assurer que le template pack est bien défini ici si besoin
        helper.template_pack = 'bulma' 
        helper.layout = Layout(
            Fieldset(
                '👤 Informations personnelles',
                Div(
                    Div(Field('text', placeholder="Ex: Jean Dupont"), css_class='column is-6'),
                    Div(Field('email', placeholder="jean@email.com"), css_class='column is-6'),
                    css_class='columns' 
                ),
                Div(
                    Div(PasswordWithIconField('password'), css_class='column is-6'),
                    Div(Field('number'), css_class='column is-6'),
                    css_class='columns'
                )
            ),
            HTML('<hr class="my-5">'),
            Div(IconField('text_with_icon', icon_prepend="fas fa-user", icon_append="fas fa-check")),
            HTML('<hr class="my-5">'),
            Fieldset(
                '🎨 Préférences visuelles',
                Div(
                    Div(ToolkitSelectField('select', icon='fa-palette'), css_class='column is-4'),
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
                    Div(FileUpload('file'), css_class='column is-4'),
                    css_class='columns'
                ),
                Div(Div(FileUpload('file2'), css_class='column is-4'),),
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
        return helper