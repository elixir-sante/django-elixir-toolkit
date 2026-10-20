from datetime import date

from django import forms
from django.utils.safestring import mark_safe
from crispy_forms.layout import Layout, Fieldset, HTML, Field, Div
from crispy_bulma.layout import IconField
from django_ckeditor_5.widgets import CKEditor5Widget
from elixir_toolkit.forms import (
    MultipleFileField,
    FileUpload,
    ToolkitFileField,
    ToolkitSelectField,
    CustomFormHelper,
    PasswordWithIconField,
)
from elixir_toolkit.validators import (
    FrenchPhoneNumberValidator,
    normalize_french_phone_number,
    FRENCH_PHONE_INPUT_PATTERN,
)

COLOR_CHOICES = (("red", "Red"), ("green", "Green"), ("blue", "Blue"))

# ---------------------------------------------------------------------------
# HACK - help_text par option d'un champ a choix multiples
# ---------------------------------------------------------------------------
# Django ne prevoit pas de help_text par option : les choices sont des
# 2-tuples et le rendu crispy-bulma affiche le libelle seul. Ce contournement
# injecte du HTML (mark_safe) dans le libelle du choix pour afficher une aide
# sous la ligne ; le CSS du toolkit l'empile sous le libelle.
#
# A utiliser UNIQUEMENT pour du texte 100% statique ecrit par vous :
# - le HTML n'est echappe nulle part : jamais de donnee utilisateur ici ;
# - pour une aide sur tout le champ, preferer le help_text standard du champ
#   (cf. checkbox_help ci-dessous), rendu par crispy sous le champ.
# ---------------------------------------------------------------------------
CHECKBOX_HELP_CHOICES = (
    (
        "red",
        mark_safe(
            "<span>Red</span>"
            '<span class="help">Couleur chaude et énergique</span>'
        ),
    ),
    ("green", "Green"),
    (
        "blue",
        mark_safe(
            "<span>Blue</span>"
            '<span class="help">Couleur froide et apaisante</span>'
        ),
    ),
)

TYPE_ACTE_CHOICES = (
    ("Consultation", "Consultation"),
    ("Pharmacie", "Pharmacie"),
    ("Hospitalisation", "Hospitalisation"),
    ("Optique", "Optique"),
    ("Dentaire", "Dentaire"),
    ("Analyses", "Analyses"),
)

VILLE_CHOICES = (
    ("Paris", "Paris"),
    ("Lyon", "Lyon"),
    ("Marseille", "Marseille"),
    ("Toulouse", "Toulouse"),
    ("Bordeaux", "Bordeaux"),
    ("Nantes", "Nantes"),
    ("Lille", "Lille"),
    ("Strasbourg", "Strasbourg"),
)

STATUT_CHOICES = (
    ("Payé", "Payé"),
    ("En attente", "En attente"),
    ("Refusé", "Refusé"),
)

# Classe commune à tous les champs du filtre, ciblée par filter_target du ui_table
LARGE_TABLE_FILTER_CLASS = "large-table-filter"


class TableFilterLargeForm(CustomFormHelper, forms.Form):
    """Filtres client du tableau « Table Filter Large ».

    Chaque widget porte data-filter-column (index de la colonne filtrée) et la classe
    LARGE_TABLE_FILTER_CLASS ; le filtrage est fait côté client par table-filter.js.
    """

    recherche = forms.CharField(
        label="Bénéficiaire ou référence",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": LARGE_TABLE_FILTER_CLASS,
                "data-filter-column": 0,
                "placeholder": "Ex: Dupont, REF-00042",
            }
        ),
    )
    type_acte = forms.ChoiceField(
        label="Type d'acte",
        required=False,
        choices=(("", "Tous les types"),) + TYPE_ACTE_CHOICES,
        widget=forms.Select(
            attrs={"class": LARGE_TABLE_FILTER_CLASS, "data-filter-column": 1}
        ),
    )
    ville = forms.ChoiceField(
        label="Ville",
        required=False,
        choices=(("", "Toutes les villes"),) + VILLE_CHOICES,
        widget=forms.Select(
            attrs={"class": LARGE_TABLE_FILTER_CLASS, "data-filter-column": 2}
        ),
    )
    statuts = forms.MultipleChoiceField(
        label="Statut",
        required=False,
        choices=STATUT_CHOICES,
        initial=[value for value, _ in STATUT_CHOICES],
        widget=forms.CheckboxSelectMultiple(
            attrs={"class": LARGE_TABLE_FILTER_CLASS, "data-filter-column": 3}
        ),
    )
    # Case unique : sa valeur est recherchée dans l'attribut data-search des lignes
    tiers_payant = forms.BooleanField(
        label="Tiers payant uniquement",
        required=False,
        widget=forms.CheckboxInput(
            attrs={"class": LARGE_TABLE_FILTER_CLASS, "value": "tiers-payant"}
        ),
    )

    @property
    def helper(self):
        helper = super().helper
        helper.template_pack = "bulma"
        helper.layout = Layout(
            Div(
                Div(Field("recherche"), css_class="column is-4"),
                Div(Field("type_acte"), css_class="column is-4"),
                Div(Field("ville"), css_class="column is-4"),
                css_class="columns",
            ),
            Div(
                Div("statuts", css_class="column is-6"),
                Div("tiers_payant", css_class="column is-6"),
                css_class="columns",
            ),
            HTML("""
                <div class="field"><div class="control">
                    <button type="reset" class="button is-light">Réinitialiser</button>
                </div></div>
            """),
        )
        return helper


class FormExample(CustomFormHelper, forms.Form):
    text = forms.CharField(label="Nom complet")
    text_with_icon = forms.CharField(label="Nom complet et icone")
    email = forms.EmailField(label="Adresse Email")
    telephone = forms.CharField(
        label="Téléphone",
        help_text="Formats acceptés : 06 12 34 56 78, +33 6 12 34 56 78... "
                  "(normalisé au format national)",
        validators=[FrenchPhoneNumberValidator()],
        widget=forms.TextInput(attrs={
            "inputmode": "tel",
            "pattern": FRENCH_PHONE_INPUT_PATTERN,
        }),
    )
    number = forms.CharField(label="Âge", widget=forms.NumberInput())
    url = forms.CharField(label="Site Web", widget=forms.URLInput())
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={"placeholder": "********"}),
    )
    select = forms.ChoiceField(label="Couleur unique", choices=COLOR_CHOICES)
    multi_select = forms.MultipleChoiceField(
        label="Couleurs multiples", choices=COLOR_CHOICES
    )
    textarea = forms.CharField(label="Message", widget=forms.Textarea())
    textarea_limite = forms.CharField(
        label="Message limité à 50 caractères",
        widget=forms.Textarea(),
        required=False,
        max_length=50,
    )
    ckeditor_limite = forms.CharField(
        label="Texte riche limité à 100 caractères",
        widget=CKEditor5Widget(config_name="light"),
        required=False,
        max_length=100,
        initial="<p>Le texte <strong>visible</strong> est compté, pas les balises HTML.</p>",
    )
    checkbox = forms.BooleanField(label="J'accepte les conditions", required=True)
    checkbox_help = forms.BooleanField(
        label="J'accepte de recevoir la newsletter",
        required=False,
        help_text="Vous pourrez vous désinscrire à tout moment depuis le lien en bas de nos emails.",
    )
    checkboxes = forms.MultipleChoiceField(
        label="Options à cocher",
        choices=CHECKBOX_HELP_CHOICES,  # HACK : cf. CHECKBOX_HELP_CHOICES
        widget=forms.CheckboxSelectMultiple(),
    )
    radios = forms.ChoiceField(
        label="Choix exclusif",
        choices=COLOR_CHOICES,
        widget=forms.RadioSelect(),
    )
    # DateField standard : input natif, placeholder grisé et croix automatiques
    date_vide = forms.DateField(label="Date d'effet", required=False)
    date_remplie = forms.DateField(
        label="Date de naissance", required=False, initial=date(1990, 5, 14)
    )
    date_disabled = forms.DateField(
        label="Date de création (désactivée)",
        required=False,
        initial=date(2024, 2, 1),
        disabled=True,
    )
    # Pièces jointes : unique via ToolkitFileField, multiples via MultipleFileField
    fichier_unique = ToolkitFileField(label="Pièce jointe unique", required=False)
    fichiers_multiples = MultipleFileField(
        label="Pièces jointes multiples", required=False
    )
    # help_text écrasé : le texte généré automatiquement est totalement remplacé
    fichier_personnalise = ToolkitFileField(
        label="Pièce jointe avec help_text personnalisé",
        max_size=10 * 1024 * 1024,
        allowed_extensions=["pdf"],
        help_text="Merci de joindre votre justificatif de domicile au format PDF (10 Mo max) <= ceci est un help_text écrasé",
        required=False,
    )

    def clean_telephone(self):
        # Un validator ne peut pas réécrire la valeur : la normalisation
        # (+33/0033 -> 06...) se fait dans le clean du champ.
        return normalize_french_phone_number(self.cleaned_data["telephone"])

    @property
    def helper(self):
        helper = super().helper

        # IMPORTANT: S'assurer que le template pack est bien défini ici si besoin
        helper.template_pack = "bulma"
        helper.layout = Layout(
            Fieldset(
                "👤 Informations personnelles",
                Div(
                    Div(
                        Field("text", placeholder="Ex: Jean Dupont"),
                        css_class="column is-6",
                    ),
                    Div(
                        Field("email", placeholder="jean@email.com"),
                        css_class="column is-6",
                    ),
                    Div(
                        Field("telephone", placeholder="06 12 34 56 78"),
                        css_class="column is-6",
                    ),
                    css_class="columns",
                ),
                Div(
                    Div(PasswordWithIconField("password"), css_class="column is-6"),
                    Div(Field("number"), css_class="column is-6"),
                    css_class="columns",
                ),
            ),
            HTML('<hr class="my-5">'),
            Div(
                IconField(
                    "text_with_icon",
                    icon_prepend="fas fa-user",
                    icon_append="fas fa-check",
                )
            ),
            HTML('<hr class="my-5">'),
            Fieldset(
                "📅 Dates",
                Div(
                    Div("date_vide", css_class="column is-4"),
                    Div("date_remplie", css_class="column is-4"),
                    Div("date_disabled", css_class="column is-4"),
                    css_class="columns",
                ),
            ),
            HTML('<hr class="my-5">'),
            Fieldset(
                "🎨 Préférences visuelles",
                Div(
                    Div(
                        ToolkitSelectField("select", icon="fa-palette"),
                        css_class="column is-4",
                    ),
                    Div("multi_select", css_class="column is-4"),
                    Div(Field("url"), css_class="column is-4"),
                    css_class="columns",
                ),
                "textarea",
                "textarea_limite",
                "ckeditor_limite",
            ),
            HTML('<hr class="my-5">'),
            Fieldset(
                "🔘 Choix et Fichiers",
                Div(
                    Div("checkboxes", css_class="column is-6"),
                    Div("radios", css_class="column is-6"),
                    css_class="columns",
                ),
                "checkbox",
                "checkbox_help",
                Div(
                    Div(FileUpload("fichier_unique"), css_class="column is-6"),
                    Div(FileUpload("fichiers_multiples"), css_class="column is-6"),
                    css_class="columns",
                ),
                Div(FileUpload("fichier_personnalise")),
            ),
            HTML("""
                <div class="field mt-5"><div class="control">
                    <button type="submit" class="button is-primary is-fullwidth">
                        <span class="icon"><i class="fas fa-paper-plane"></i></span>
                        <span>Envoyer le formulaire</span>
                    </button>
                </div></div>
            """),
        )
        return helper


class FormErrorsExample(CustomFormHelper, forms.Form):
    """Démonstration de l'UI des erreurs de validation.

    Avec les données de démonstration (cf. FormErrorsTestView.DEMO_DATA),
    chaque champ échoue avec un type d'erreur différent (requis, format,
    min/max, longueur) et `clean` ajoute des erreurs globales.
    """

    text = forms.CharField(label="Nom complet", min_length=3)
    email = forms.EmailField(label="Adresse email")
    telephone = forms.CharField(
        label="Téléphone",
        validators=[FrenchPhoneNumberValidator()],
        widget=forms.TextInput(attrs={
            "inputmode": "tel",
            "pattern": FRENCH_PHONE_INPUT_PATTERN,
        }),
    )
    number = forms.IntegerField(label="Âge", min_value=0, max_value=120)
    url = forms.URLField(label="Site web")
    password = forms.CharField(
        label="Mot de passe",
        min_length=12,
        widget=forms.PasswordInput(attrs={"placeholder": "********"}),
    )
    select = forms.ChoiceField(label="Couleur unique", choices=COLOR_CHOICES)
    multi_select = forms.MultipleChoiceField(
        label="Couleurs multiples", choices=COLOR_CHOICES
    )
    date_effet = forms.DateField(label="Date d'effet")
    textarea = forms.CharField(label="Message", max_length=100, widget=forms.Textarea())
    checkbox = forms.BooleanField(label="J'accepte les conditions")
    checkboxes = forms.MultipleChoiceField(
        label="Options à cocher", choices=COLOR_CHOICES, widget=forms.CheckboxSelectMultiple()
    )
    radios = forms.ChoiceField(
        label="Choix exclusif", choices=COLOR_CHOICES, widget=forms.RadioSelect()
    )
    fichier = ToolkitFileField(label="Pièce jointe", allowed_extensions=["pdf"])

    def __init__(self, *args, show_global_errors=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.show_global_errors = show_global_errors

    def clean(self):
        super().clean()
        if self.show_global_errors and self.errors:
            self.add_error(
                None,
                "Le formulaire comporte des erreurs de validation : "
                "merci de corriger les champs signalés en rouge.",
            )
            self.add_error(
                None,
                "Erreur globale non rattachée à un champ : "
                "les données saisies sont incohérentes entre elles.",
            )

    @property
    def helper(self):
        helper = super().helper
        helper.template_pack = "bulma"
        helper.layout = Layout(
            Fieldset(
                "👤 Informations personnelles",
                Div(
                    Div(Field("text", placeholder="Ex: Jean Dupont"), css_class="column is-6"),
                    Div(Field("email", placeholder="jean@email.com"), css_class="column is-6"),
                    Div(Field("telephone", placeholder="06 12 34 56 78"), css_class="column is-6"),
                    css_class="columns",
                ),
                Div(
                    Div(PasswordWithIconField("password"), css_class="column is-6"),
                    Div(Field("number"), css_class="column is-6"),
                    css_class="columns",
                ),
                Div(
                    Div(Field("url"), css_class="column is-6"),
                    Div("date_effet", css_class="column is-6"),
                    css_class="columns",
                ),
            ),
            HTML('<hr class="my-5">'),
            Fieldset(
                "🎨 Préférences et pièces jointes",
                Div(
                    Div(ToolkitSelectField("select", icon="fa-palette"), css_class="column is-6"),
                    Div("multi_select", css_class="column is-6"),
                    css_class="columns",
                ),
                "textarea",
                Div(
                    Div("checkboxes", css_class="column is-6"),
                    Div("radios", css_class="column is-6"),
                    css_class="columns",
                ),
                Div("checkbox", FileUpload("fichier")),
            ),
            HTML("""
                <div class="field mt-5"><div class="control">
                    <button type="submit" class="button is-primary is-fullwidth">
                        <span class="icon"><i class="fas fa-paper-plane"></i></span>
                        <span>Soumettre le formulaire</span>
                    </button>
                </div></div>
            """),
        )
        return helper
