from datetime import date

from django import forms
from crispy_forms.layout import Layout, Fieldset, HTML, Field, Div
from crispy_bulma.layout import IconField
from django_ckeditor_5.widgets import CKEditor5Widget
from elixir_toolkit.forms import MultipleFileField, FileUpload, ToolkitSelectField, CustomFormHelper, PasswordWithIconField


COLOR_CHOICES = (
    ('red', 'Red'), ('green', 'Green'), ('blue', 'Blue')
)

TYPE_ACTE_CHOICES = (
    ('Consultation', 'Consultation'),
    ('Pharmacie', 'Pharmacie'),
    ('Hospitalisation', 'Hospitalisation'),
    ('Optique', 'Optique'),
    ('Dentaire', 'Dentaire'),
    ('Analyses', 'Analyses'),
)

VILLE_CHOICES = (
    ('Paris', 'Paris'),
    ('Lyon', 'Lyon'),
    ('Marseille', 'Marseille'),
    ('Toulouse', 'Toulouse'),
    ('Bordeaux', 'Bordeaux'),
    ('Nantes', 'Nantes'),
    ('Lille', 'Lille'),
    ('Strasbourg', 'Strasbourg'),
)

STATUT_CHOICES = (
    ('Payé', 'Payé'),
    ('En attente', 'En attente'),
    ('Refusé', 'Refusé'),
)

# Classe commune à tous les champs du filtre, ciblée par filter_target du ui_table
LARGE_TABLE_FILTER_CLASS = 'large-table-filter'


class TableFilterLargeForm(CustomFormHelper, forms.Form):
    """Filtres client du tableau « Table Filter Large ».

    Chaque widget porte data-filter-column (index de la colonne filtrée) et la classe
    LARGE_TABLE_FILTER_CLASS ; le filtrage est fait côté client par table-filter.js.
    """
    recherche    = forms.CharField(
                    label="Bénéficiaire ou référence",
                    required=False,
                    widget=forms.TextInput(attrs={
                        'class': LARGE_TABLE_FILTER_CLASS,
                        'data-filter-column': 0,
                        'placeholder': "Ex: Dupont, REF-00042",
                    }),
                )
    type_acte    = forms.ChoiceField(
                    label="Type d'acte",
                    required=False,
                    choices=(('', "Tous les types"),) + TYPE_ACTE_CHOICES,
                    widget=forms.Select(attrs={'class': LARGE_TABLE_FILTER_CLASS, 'data-filter-column': 1}),
                )
    ville        = forms.ChoiceField(
                    label="Ville",
                    required=False,
                    choices=(('', "Toutes les villes"),) + VILLE_CHOICES,
                    widget=forms.Select(attrs={'class': LARGE_TABLE_FILTER_CLASS, 'data-filter-column': 2}),
                )
    statuts      = forms.MultipleChoiceField(
                    label="Statut",
                    required=False,
                    choices=STATUT_CHOICES,
                    initial=[value for value, _ in STATUT_CHOICES],
                    widget=forms.CheckboxSelectMultiple(attrs={'class': LARGE_TABLE_FILTER_CLASS, 'data-filter-column': 3}),
                )
    # Case unique : sa valeur est recherchée dans l'attribut data-search des lignes
    tiers_payant = forms.BooleanField(
                    label="Tiers payant uniquement",
                    required=False,
                    widget=forms.CheckboxInput(attrs={'class': LARGE_TABLE_FILTER_CLASS, 'value': 'tiers-payant'}),
                )

    @property
    def helper(self):
        helper = super().helper
        helper.template_pack = 'bulma'
        helper.layout = Layout(
            Div(
                Div(Field('recherche'), css_class='column is-4'),
                Div(Field('type_acte'), css_class='column is-4'),
                Div(Field('ville'), css_class='column is-4'),
                css_class='columns'
            ),
            Div(
                Div('statuts', css_class='column is-6'),
                Div('tiers_payant', css_class='column is-6'),
                css_class='columns'
            ),
            HTML("""
                <div class="field"><div class="control">
                    <button type="reset" class="button is-light">Réinitialiser</button>
                </div></div>
            """)
        )
        return helper

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
    textarea_limite = forms.CharField(label="Message limité à 50 caractères", widget=forms.Textarea(), required=False, max_length=50)
    ckeditor_limite = forms.CharField(
                        label="Texte riche limité à 100 caractères",
                        widget=CKEditor5Widget(config_name='light'),
                        required=False,
                        max_length=100,
                        initial="<p>Le texte <strong>visible</strong> est compté, pas les balises HTML.</p>",
                    )
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
    # DateField standard : input natif, placeholder grisé et croix automatiques
    date_vide       = forms.DateField(label="Date d'effet", required=False)
    date_remplie    = forms.DateField(label="Date de naissance", required=False, initial=date(1990, 5, 14))
    date_disabled   = forms.DateField(label="Date de création (désactivée)", required=False, initial=date(2024, 2, 1), disabled=True)
    # file = MultipleFileField(label="Documents justificatifs", required=True)
    # file2 = forms.FileField(label="Documents test", required=True)

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
                '📅 Dates',
                Div(
                    Div('date_vide', css_class='column is-4'),
                    Div('date_remplie', css_class='column is-4'),
                    Div('date_disabled', css_class='column is-4'),
                    css_class='columns'
                )
            ),
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
                'textarea_limite',
                'ckeditor_limite',
            ),
            HTML('<hr class="my-5">'),
            Fieldset(
                '🔘 Choix et Fichiers',
                Div(
                    Div('checkboxes', css_class='column is-4'),
                    Div('radios', css_class='column is-4'),
                    # On repasse en mode explicite pour éviter le bug de détection
                    # Div(FileUpload('file'), css_class='column is-4'),
                    # css_class='columns'
                ),
                # Div(Div(FileUpload('file2'), css_class='column is-4'),),
                # 'checkbox',
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