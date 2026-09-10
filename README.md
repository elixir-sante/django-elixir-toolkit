# Django Elixir Toolkit

**Django Elixir Toolkit** est une bibliothèque de composants UI réutilisables pour Django, basée sur le framework CSS **Bulma** et optimisée pour **Django Crispy Forms** avec **crispy-bulma**.

Copyright (C) 2026 Elixir Santé

---

## Installation

### 1. Installation via pip

* **Production (version spécifique) :**
```bash
pip install git+https://github.com/elixir-sante/django-elixir-toolkit.git@v0.17.9
```

* **Développement (dernières nouveautés) :**
```bash
pip install git+https://github.com/elixir-sante/django-elixir-toolkit.git@dev
```

### 2. Configuration Django

Ajoutez les applications nécessaires dans votre `settings.py` :

```python
INSTALLED_APPS = [
    ...
    'crispy_forms',
    'crispy_bulma',
    'elixir_toolkit',
    ...
]

CRISPY_ALLOWED_TEMPLATE_PACKS = "bulma"
CRISPY_TEMPLATE_PACK = "bulma"
```

### 3. Chargement des ressources

Dans votre template de base, chargez les CSS et JS nécessaires :

```html
{% load elixir_toolkit_tags %}
{% toolkit_css %}
```

Ce tag charge automatiquement :
- Bulma CSS (via CDN)
- Font Awesome (via CDN)
- Selectize CSS/JS (via CDN)
- jQuery (via CDN)
- Tous les CSS/JS personnalisés du toolkit

---

## Structure du Projet

```
elixir_toolkit/
├── templatetags/
│   └── elixir_toolkit_tags.py    # Tags personnalisés pour les composants
├── templates/
│   └── elixir_toolkit/
│       ├── components/
│       │   ├── button.html        # Boutons
│       │   ├── chevron.html       # Icônes de direction
│       │   ├── filter_bar.html     # Barre de filtres
│       │   ├── list.html           # Liste d'éléments
│       │   ├── select.html         # Sélecteur avec Selectize
│       │   ├── table.html          # Tableau
│       │   ├── tabs_scroll_hints.html # Indicateurs de défilement
│       │   ├── tag.html            # Badge/Tag
│       │   ├── td.html             # Cellule de tableau
│       │   ├── th.html             # En-tête de tableau
│       │   └── toolkit_css.html     # Chargement des ressources
│       └── components/fields/
│           ├── file_input.html     # Champ de fichier
│           └── password_input.html # Champ mot de passe
├── static/
│   ├── css/toolkit/              # CSS personnalisés
│   │   ├── button.css
│   │   ├── bulma-list.css
│   │   ├── ckeditor.css
│   │   ├── selectize.css
│   │   ├── spinner.css
│   │   └── tabs.css
│   └── js/toolkit/               # JavaScript
│       ├── ckeditor-clipboard-manager.js
│       ├── ckeditor-load-external-plugins.js
│       ├── ckeditor-upload-adapter.js
│       ├── fields-dependencies.js
│       └── tabs-scroll-hints.js
└── forms.py                     # Champs et helpers
```

---

## Composants Disponibles

### Boutons

#### Bouton standard
```html
{% load elixir_toolkit_tags %}
{% ui_button text="Enregistrer" css_classes="is-success" %}
```

#### Bouton avec icône
```html
{% ui_button text="Voir la documentation" href="https://bulma.io" target="_blank" icon="fas fa-book" %}
```

#### Bouton avec icône à droite
```html
{% ui_button text="Suivant" icon="fas fa-arrow-right" icon_right=True %}
```

#### Bouton primaire
```html
{% ui_button_primary text="Valider" %}
```

#### Bouton secondaire (outlined)
```html
{% ui_button_secondary text="Annuler" %}
```

**Paramètres :**
- `text` : Texte du bouton (requis)
- `css_classes` : Classes CSS supplémentaires
- `icon` : Classe Font Awesome (ex: `fas fa-book`)
- `icon_right` : Icône à droite (booléen)
- `href` : URL pour un lien
- `target` : Cible du lien
- `type` : Type du bouton
- Autres attributs HTML via kwargs

---

### Sélecteur (Selectize)

#### Sélecteur simple
```html
{% ui_select name="category" options=[("1", "Catégorie 1"), ("2", "Catégorie 2")] %}
```

#### Sélecteur avec valeur présélectionnée
```html
{% ui_select name="status" options=[("active", "Actif")] selected="active" %}
```

#### Sélecteur multiple
```html
{% ui_select name="tags" options=[("1", "Tag 1")] multiple=True %}
```

**Paramètres :**
- `name` : Nom du champ (requis)
- `options` : Liste de tuples `(valeur, libellé)`
- `selected` : Valeur présélectionnée
- `multiple` : Mode multiple
- `placeholder` : Texte du placeholder
- `icon` : Classe Font Awesome
- `css_classes` : Classes CSS

---

### Barre de Filtres

#### Barre simple
```html
{% ui_filter_bar filters=[("active", "Actifs"), ("inactive", "Inactifs")] %}
```

#### Avec groupes
```html
{% ui_filter_bar filters=[[("a", "A"), ("b", "B")], [("x", "X"), ("y", "Y")]] %}
```

**Paramètres :**
- `filters` : Liste de tuples ou liste de listes
- `identifier` : Identifiant unique

---

### Liste d'Éléments

#### Liste simple
```html
{% ui_list items=object_list title_field="name" desc_field="description" %}
```

#### Avec icônes et tags
```html
{% ui_list items=projects title_field="title" icon_field="icon" tag_label_field="status" %}
```

**Paramètres :**
- `items` : Liste d'objets (requis)
- `title_field` : Champ pour le titre
- `desc_field` : Champ pour la description
- `icon_field` : Champ pour l'icône
- `tag_label_field` : Champ pour le tag
- `link_url_name` : Nom de l'URL Django

---

### Tableau

#### Tableau simple
```html
{% ui_table %}
    <thead>
        <tr>
            {% ui_th %}Nom{% end_ui_th %}
        </tr>
    </thead>
    <tbody>
        <tr>
            {% ui_td %}Valeur{% end_ui_td %}
        </tr>
    </tbody>
{% end_ui_table %}
```

#### Tableau expandable
```html
{% ui_table expandable=True css_classes="is-striped" %}
    ...
{% end_ui_table %}
```

**Paramètres :**
- `css_classes` : Classes CSS
- `expandable` : Mode expandable

---

### Tag / Badge

```html
{% ui_tag text="Actif" color="success" %}
{% ui_tag text="Validé" color="info" icon="fas fa-check" %}
```

**Paramètres :**
- `text` : Texte (requis)
- `color` : Couleur Bulma
- `icon` : Classe Font Awesome
- `dot` : Affiche un point (booléen)

---

### Chevron

```html
{% ui_chevron direction="right" %}
{% ui_chevron direction="down" size="small" %}
```

**Paramètres :**
- `direction` : `down`, `right`, `up`, `left`
- `size` : Taille

---

### Indicateurs de Défilement pour Onglets

```html
<div class="tabs-scroll-wrapper">
    <div class="tabs">...</div>
    {% ui_tabs_scroll_hints %}
</div>
```

---

## Champs de Formulaire

### Champ de Fichier avec Upload

```python
from elixir_toolkit.forms import FileUpload, ToolkitFileField

class MyForm(forms.Form):
    document = ToolkitFileField(
        max_size=10 * 1024 * 1024,  # 10 Mo
        allowed_extensions=['pdf', 'png', 'jpg']
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            FileUpload('document'),
        )
```

**Paramètres de `ToolkitFileField` :**
- `max_size` : Taille maximale par fichier (défaut: 5 Mo)
- `allowed_extensions` : Extensions autorisées (défaut: `['pdf', 'png', 'jpg', 'jpeg']`)

---

### Champ Mot de Passe avec Toggle

```python
from elixir_toolkit.forms import PasswordWithIconField

class MyForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            PasswordWithIconField('password'),
        )
```

Affiche une icône de cadenas à gauche et un bouton toggle à droite.

---

### Sélecteur avec Crispy Forms

```python
from elixir_toolkit.forms import ToolkitSelectField

class MyForm(forms.Form):
    category = forms.ChoiceField(choices=[('1', 'Catégorie 1')])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            ToolkitSelectField('category', icon='fas fa-tag'),
        )
```

---

### Helpers de Formulaire

#### SuperFormHelper

```python
from elixir_toolkit.forms import SuperFormHelper

class MyForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = SuperFormHelper()
        self.helper.enable_form_validator = True  # Validation visuelle
        self.helper.enable_submit_button_loading = True  # is-loading au submit
```

#### CustomFormHelper

Helper prêt à l'emploi avec les fonctionnalités activées :

```python
from elixir_toolkit.forms import CustomFormHelper

class MyForm(forms.Form):
    helper = CustomFormHelper()
```

---

## Validateurs

```python
from elixir_toolkit.validators import (
    MaxFileSizeValidator,
    MaxTotalSizeValidator,
    AllowedExtensionsValidator,
    MaxFilesValidator,
)

class MyForm(forms.Form):
    file = forms.FileField(
        validators=[
            MaxFileSizeValidator(10 * 1024 * 1024),
            AllowedExtensionsValidator(['pdf', 'png']),
        ]
    )
```

---

## Exemple Complet

### Template
```html
{% load elixir_toolkit_tags %}
{% toolkit_css %}

<div class="container">
    <h1 class="title">Bienvenue</h1>
    
    <div class="buttons">
        {% ui_button_primary text="Ajouter" icon="fas fa-plus" %}
        {% ui_button_secondary text="Exporter" icon="fas fa-download" %}
    </div>
    
    {% ui_filter_bar filters=[("all", "Tous"), ("active", "Actifs")] %}
    
    {% ui_list items=projects title_field="name" desc_field="description" %}
    
    {% ui_table css_classes="is-striped" %}
        <thead>
            <tr>
                {% ui_th %}Nom{% end_ui_th %}
                {% ui_th %}Statut{% end_ui_th %}
            </tr>
        </thead>
        <tbody>
            {% for item in items %}
            <tr>
                {% ui_td %}{{ item.name }}{% end_ui_td %}
                {% ui_td %}{% ui_tag text=item.status color="success" %}{% end_ui_td %}
            </tr>
            {% endfor %}
        </tbody>
    {% end_ui_table %}
</div>
```

### Formulaire
```python
from django import forms
from elixir_toolkit.forms import CustomFormHelper, ToolkitFileField
from crispy_forms.layout import Layout, Submit

class MyForm(forms.Form):
    name = forms.CharField(label="Nom")
    document = ToolkitFileField(label="Document")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = CustomFormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'name',
            FileUpload('document'),
            Submit('submit', 'Enregistrer', css_class='button is-primary')
        )
```

---

## Dépendances

- Django 3.2+
- django-crispy-forms
- crispy-bulma
- Bulma CSS
- Font Awesome
- jQuery
- Selectize.js

---

## Historique des Versions

- **v0.18.0** : Ajout des icon dans le composant ui_tag
- **v0.17.9** : Correction de la date dans le format de date
- **v0.17.8** : Fix du bug Selectize avec HTMX beforeSwap
- **v0.17.7** : Amélioration de Selectize pour HTMX
- **v0.17.6** : Correction des messages d'erreur pour les gros fichiers
- **v0.17.5** : Nouvelle version après fix fileupload

---

## Contribution

Pour contribuer au projet :

1. Forker le dépôt
2. Créer une branche pour votre fonctionnalité (`git checkout -b feature/ma-fonctionnalite`)
3. Commiter vos changements (`git commit -m 'Ajout de ma fonctionnalité'`)
4. Pousser vers la branche (`git push origin feature/ma-fonctionnalite`)
5. Ouvrir une Pull Request

---

## Licence

Ce projet est sous **licence LGPL-3.0** (GNU Lesser General Public License version 3).

**Points essentiels de la LGPL :**
- **Liberté d'utilisation** : Vous pouvez utiliser, modifier et distribuer le code
- **Obligation de mention** : Vous devez conserver les mentions de copyright et de licence
- **Modifications ouvertes** : Si vous modifiez le code source, vous devez publier vos modifications sous LGPL
- **Lien dynamique autorisé** : Vous pouvez lier cette bibliothèque à des logiciels propriétaires sans ouvrir leur code
- **Pas de contrainte sur l'application finale** : Votre application utilisant cette bibliothèque n'est pas obligée d'être open source

Voir le fichier [LICENSE](LICENSE) pour le texte complet de la licence.

---

## Support

Pour toute question ou problème, veuillez ouvrir une issue sur GitHub.
