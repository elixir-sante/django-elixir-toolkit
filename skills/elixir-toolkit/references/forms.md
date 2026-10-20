# Référence : formulaires, helpers et validateurs

Tous les imports proviennent de `elixir_toolkit.forms` ou `elixir_toolkit.validators`.

## Patchs automatiques (au chargement de l'app)

L'app patche le Django standard dès qu'elle est dans `INSTALLED_APPS`. Il faut retenir
**ce qu'il ne faut PAS refaire** :

### Champ date

`forms.DateInput` est rendu en `<input type="date">` natif avec valeur au format ISO
(`2024-02-01`), placeholder « jj/mm/aaaa » grisé et croix de réinitialisation (déclenche
`input`/`change`, compatible HTMX).

```python
class MyForm(forms.Form):
    date_effet = forms.DateField(label="Date d'effet", required=False)  # suffisant
```

- un `format=` explicite reste prioritaire (`forms.DateInput(format="%d/%m/%Y")`)
- `DateTimeInput` et `TimeInput` ne sont PAS modifiés
- pour garder un champ texte : `widget=forms.TextInput`
- libellé de la croix : `attrs={"data-clear-label": "Effacer la date d'effet"}`

### Limite de caractères

`forms.CharField` est patché : `max_length` suffit. Fonctionne pour `input`, `textarea` et
`CKEditor5Field` (frappe bloquée, collage tronqué, compteur « n / 400 caractères » en rouge
à la limite, compteur CKEditor remplaçant celui de django_ckeditor_5).

```python
# Modèle — repris automatiquement par les ModelForm (migration sans effet en base)
class Insurer(models.Model):
    config_first_login_message_content = CKEditor5Field(max_length=400, blank=True)
    note = models.TextField(max_length=400, blank=True)

# Ou directement dans le formulaire
class MyForm(forms.Form):
    message = forms.CharField(max_length=400, widget=forms.Textarea)
```

- validation serveur : le `MaxLengthValidator` de Django est remplacé par
  `RichTextMaxLengthValidator` (CKEditor : balises ignorées, entité = 1 caractère) ou
  `TextMaxLengthValidator` (retour à la ligne = 1 caractère), selon le widget
- contenu déjà trop long (valeur en base) : message d'erreur + boutons submit désactivés
- messages personnalisés :
  ```python
  message = forms.CharField(
      max_length=400,
      widget=forms.Textarea(attrs={"data-max-length-message": "Le message est limité à 400 caractères."}),
      error_messages={"max_length": "Le message est limité à 400 caractères."},
  )
  ```
- limite dynamique (connue à l'init du formulaire) :
  ```python
  from elixir_toolkit.forms import limit_length

  class MyForm(forms.Form):
      def __init__(self, *args, **kwargs):
          super().__init__(*args, **kwargs)
          limit_length(self.fields["message"], self.get_limit())
  ```
- brancher du code sur les éditeurs CKEditor :
  ```js
  window.elixirOnCkeditorReady(function (editor) {
      // appelé une fois par éditeur, existant ou créé plus tard (HTMX)
  });
  ```
  Ne pas utiliser `ckeditorRegisterCallback` de django_ckeditor_5 : déjà réservé par le toolkit.

---

## Helpers crispy

```python
from elixir_toolkit.forms import SuperFormHelper, CustomFormHelper

class MyForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = SuperFormHelper()
        self.helper.enable_form_validator = True         # classe input-error sur champ invalide
        self.helper.enable_submit_button_loading = True  # is-loading sur le bouton au submit
```

`CustomFormHelper` est un helper prêt à l'emploi (validation + loading activés,
`form_tag = False`) :

```python
class MyForm(forms.Form):
    helper = CustomFormHelper()   # attention : form_tag=False → <form> à écrire dans le template
```

Il réutilise `self.layout` si le formulaire définit un attribut `layout`.

---

## Upload de fichiers

```python
from crispy_forms.layout import Layout
from elixir_toolkit.forms import FileUpload, ToolkitFileField, MultipleFileField

class MyForm(forms.Form):
    document = ToolkitFileField(
        max_size=10 * 1024 * 1024,          # défaut : 5 Mo
        allowed_extensions=["pdf", "png"],  # défaut : ['pdf', 'png', 'jpg', 'jpeg']
    )
    pieces = MultipleFileField(
        max_size=5 * 1024 * 1024,           # par fichier
        max_total_size=5 * 1024 * 1024,     # total, défaut 5 Mo
        allowed_extensions=["pdf"],
        max_files=5,                        # défaut : 5
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = CustomFormHelper()
        self.helper.layout = Layout(
            FileUpload("document"),
            FileUpload("pieces"),
        )
```

Points importants :

- **`FileUpload('champ')` dans le `Layout` crispy est obligatoire** : c'est lui qui branche
  le bon widget (`MultipleFileUploadInput` / `SingleFileInput`) et le rendu stylé
  (glisser-déposer, messages d'erreur). Ne pas rendre le champ avec un `{{ form.document }}`
  brut ni un autre `Field` crispy.
- `ToolkitFileField` refuse plusieurs fichiers dans un champ unique (erreur
  « Vous ne pouvez joindre qu'un seul fichier. ») ; ne pas ajouter soi-même les validateurs,
  ils sont déjà injectés (`MaxFileSizeValidator`, `AllowedExtensionsValidator`).
- `MultipleFileField` ajoute en plus `MaxTotalSizeValidator` et `MaxFilesValidator`.
- Les attributs `data-max-size`, `data-allowed-extensions`, `data-max-files` posés sur le
  widget alimentent la validation côté navigateur.
- **`help_text` généré automatiquement** à partir des paramètres d'appel du champ
  (`max_size`, `allowed_extensions`, et pour `MultipleFileField` `max_files` /
  `max_total_size`) :
  - `ToolkitFileField` : « 5 Mo maximum. Formats acceptés : PDF, PNG, JPG, JPEG. »
  - `MultipleFileField` : « 5 fichiers maximum. 5 Mo maximum par fichier (5 Mo au total).
    Formats acceptés : PDF, PNG, JPG, JPEG. »

  Le texte reflète les valeurs réellement passées. Le passer explicitement l'écrase
  totalement — ne l'écrire à la main que pour un texte métier spécifique, pas pour
  reformuler les limites.

---

## Champs crispy stylés

```python
from elixir_toolkit.forms import PasswordWithIconField, ToolkitSelectField

# Mot de passe : cadenas à gauche, bouton toggle à droite
self.helper.layout = Layout(
    PasswordWithIconField("password"),
)

# Select (Selectize) : lit choices / valeur / placeholder automatiquement
self.helper.layout = Layout(
    ToolkitSelectField("category", icon="fas fa-tag", css_classes=""),
)
```

`ToolkitSelectField` détecte seul le mode multiple (`MultipleChoiceField`,
`ModelMultipleChoiceField`) et prend `empty_label` du champ comme placeholder
(défaut « Sélectionnez une option... »). Le champ Django reste un `ChoiceField` standard.

### Checkboxes et radios stylés

`{% toolkit_assets %}` charge `bulma-checkbox.css` / `bulma-radio.css` : tout
`<label class="checkbox">` / `<label class="radio">` (rendu crispy compris) est
stylé automatiquement. Couleurs et tailles par classes Bulma sur le `<label>`
(`is-primary`, `is-small`, ...). La couleur primaire (défaut et `is-primary`)
suit `var(--bulma-primary)` du thème. Le `help_text` du champ reste standard
(rendu par crispy sous le champ).

**Hack — help_text par option** (Django ne le prévoit pas ; dernier recours, texte
100% statique écrit par vous, jamais de donnée utilisateur — le HTML n'est
échappé nulle part) :

```python
from django.utils.safestring import mark_safe

checkboxes = forms.MultipleChoiceField(
    label="Options à cocher",
    choices=(
        ("red", mark_safe("<span>Red</span>"
                          '<span class="help">Couleur chaude et énergique</span>')),
        ("green", "Green"),
    ),
    widget=forms.CheckboxSelectMultiple(),
)
```

Le CSS du toolkit affiche l'aide sous le libellé. Préférer le `help_text` du
champ quand l'aide porte sur tout le champ.

---

## Validateurs

```python
from elixir_toolkit.validators import (
    MaxFileSizeValidator,       # (max_size) — par fichier
    MaxTotalSizeValidator,      # (max_total_size) — sur l'ensemble des fichiers
    AllowedExtensionsValidator, # (['pdf', 'png'])
    MaxFilesValidator,          # (max_files)
    TextMaxLengthValidator,     # (limit_value) — texte brut, \r\n = 1 caractère
    RichTextMaxLengthValidator, # (limit_value) — HTML : texte visible uniquement
    NIRValidator,               # numéro de sécurité sociale français
    FrenchPhoneNumberValidator,  # téléphone français : 06..., +33 6..., 0033...
    normalize_french_phone_number,  # réécrit +33/0033 en national (06...) — dans clean()
    FRENCH_PHONE_INPUT_PATTERN,  # pattern HTML5 (attribut `pattern`) pour la validation navigateur
    FRENCH_PHONE_INPUT_TITLE,    # message `title` HTML5 par défaut (optionnel)
    IBANValidator, FrenchIBANValidator,
    is_valid_iban, get_iban_country, get_iban_check_digits,
)
```

Les validateurs de fichiers acceptent un fichier seul ou une liste. Ils sont comparables
entre eux (`__eq__`/`__hash__`) pour ne pas générer de migrations en boucle.

## Téléphone français

```python
from elixir_toolkit.validators import FrenchPhoneNumberValidator, normalize_french_phone_number

class MyForm(forms.Form):
    # Accepte 0612345678, "06 12 34 56 78", "+33 6 12 34 56 78", "0033 6 12 34 56 78"...
    phone = forms.CharField(validators=[FrenchPhoneNumberValidator()])

    def clean_phone(self):
        # Un validator ne peut pas réécrire la valeur : la normalisation
        # (+33/0033 -> 06...) se fait ici, dans le clean du champ.
        return normalize_french_phone_number(self.cleaned_data["phone"])
```

Les valeurs vides ne sont pas validées (rôle de `blank`/`required`).

### Validation front (HTML5)

Le navigateur peut bloquer la soumission avant tout aller-retour serveur via
l'attribut `pattern` (le regex est implicitement ancré `^...$`). `type="tel"`
seul ne valide rien, c'est le `pattern` qui travaille. Sans attribut `title`
explicite, le navigateur affiche son message générique : poser le format
attendu dans le `placeholder`/`help_text` du champ :

```python
telephone = forms.CharField(
    validators=[FrenchPhoneNumberValidator()],  # sécurité côté serveur, toujours
    widget=forms.TextInput(attrs={
        "inputmode": "tel",
        "pattern": FRENCH_PHONE_INPUT_PATTERN,
    }),
)
```

La validation front est un confort UX uniquement : elle est contournable
(JS désactivé, requête forgée). Garder le validator Django en parallèle.
