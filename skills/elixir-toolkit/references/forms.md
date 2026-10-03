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
    IBANValidator, FrenchIBANValidator,
    is_valid_iban, get_iban_country, get_iban_check_digits,
)
```

Les validateurs de fichiers acceptent un fichier seul ou une liste. Ils sont comparables
entre eux (`__eq__`/`__hash__`) pour ne pas générer de migrations en boucle.
