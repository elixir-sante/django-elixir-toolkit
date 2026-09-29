# Référence : tags de template

Tous les tags ci-dessous sont dans la librairie `elixir_toolkit_tags`, sauf mention contraire.

```html
{% load elixir_toolkit_tags %}
```

Conventions : les paramètres sont listés avec leur valeur par défaut. Les classes CSS
attendues sont des classes Bulma (`is-primary`, `is-success`, `is-striped`, ...).

---

## {% toolkit_assets version="1.0.0" %}

Charge tout le nécessaire : Bulma (CDN, version = paramètre), Font Awesome, Selectize,
jQuery, Tablesorter, et les CSS/JS du toolkit. À placer une seule fois dans le template de
base, idéalement dans `<head>`. Ne pas ré-inclure ces ressources ailleurs.

---

## Boutons

```html
{% ui_button text="Enregistrer" css_classes="is-success" %}
{% ui_button text="Docs" href="https://bulma.io" target="_blank" icon="fas fa-book" %}
{% ui_button text="Suivant" icon="fas fa-arrow-right" icon_right=True %}
{% ui_button_primary text="Valider" %}
{% ui_button_secondary text="Annuler" %}
```

- `text` : libellé (requis dans la pratique)
- `css_classes` : classes supplémentaires (`ui_button_primary` ajoute `is-primary`,
  `ui_button_secondary` ajoute `is-primary is-outlined`)
- `icon` : classe Font Awesome (`fas fa-book`), affichée à gauche par défaut
- `icon_right` : `True` pour l'icône à droite
- `href` : transforme le bouton en lien ; `target` accepté
- `type` : type du bouton (défaut `button`)
- kwargs supplémentaires → attributs HTML, underscores convertis en tirets
  (`data_id="x"` → `data-id="x"`)

---

## Sélecteur (Selectize)

```html
{% ui_select name="category" options=[("1", "Catégorie 1"), ("2", "Catégorie 2")] %}
{% ui_select name="status" options=opts selected="active" %}
{% ui_select name="tags" options=opts multiple=True placeholder="Choisir..." icon="fas fa-tag" %}
```

- `name` (requis) : nom du champ ; `id` généré : `id_{name}` (ou `element_id` explicite)
- `options` (requis) : liste de tuples `(valeur, libellé)` ; accepte aussi un dict ou une
  chaîne littérale Python
- `selected` : valeur présélectionnée
- `multiple` : sélection multiple
- `placeholder` : défaut `"Choisissez..."`
- `icon` : classe Font Awesome dans le champ
- `css_classes` : classes supplémentaires

Dans un formulaire crispy, préférer `ToolkitSelectField` (cf. `forms.md`) : il lit les
`choices` et la valeur du champ automatiquement.

---

## Barre de filtres

```html
{% ui_filter_bar filters=[("active", "Actifs"), ("inactive", "Inactifs")] %}
{% ui_filter_bar filters=[[("a", "A"), ("b", "B")], [("x", "X")]] %}
```

- `filters` (requis) : liste de tuples, ou liste de listes de tuples (groupes)
- `identifier` : identifiant unique (défaut `"default"`), utile si plusieurs barres

---

## Liste d'éléments

```html
{% ui_list items=object_list title_field="name" desc_field="description" %}
{% ui_list items=projects title_field="title" icon_field="icon" tag_label_field="status" link_url_name="project-detail" %}
```

- `items` (requis) : liste d'objets (attributs lus via `getattr`, ou dicts via `.get`)
- `title_field` (défaut `"title"`), `desc_field` (défaut `"description"`)
- `extra_field` : champ supplémentaire
- `icon_field` : icône (défaut `"receipt"` si absent)
- `tag_label_field`, `tag_icon_field` (défaut `"user"`) : badge sur l'élément
- `link_url_name` : nom d'URL Django pour rendre l'élément cliquable
- `css_classes` : classes supplémentaires

---

## Tableau

Tag à bloc. Le contenu brut `<thead>`/`<tbody>` va à l'intérieur, les cellules via `ui_th`/`ui_td`.

```html
{% ui_table orderable=True css_classes="is-striped is-narrow" %}
    <thead>
        <tr>
            {% ui_th %}Produit{% end_ui_th %}
            {% ui_th orderable=False %}Actions{% end_ui_th %}
        </tr>
    </thead>
    <tbody>
        <tr>
            {% ui_td css_classes="pl-5" %}Produit 1{% end_ui_td %}
            {% ui_td %}<a href="...">Modifier</a>{% end_ui_td %}
        </tr>
    </tbody>
{% end_ui_table %}
```

Paramètres :

- `css_classes` : classes Bulma du `<table>` (le toolkit ajoute `table is-fullwidth is-hoverable`)
- `id` : attribut `id` du `<table>`
- `orderable=True` : tri des colonnes (Tablesorter, chargé par `toolkit_assets`).
  `ui_th` participe au tri par défaut ; `orderable=False` sur un `ui_th` l'exclut.
- `expandable=True` : active le JS d'expansion de lignes (voir plus bas)
- `filterable=True` : filtrage client, avec :
  - `filter_target="#mon-input"` : sélecteur du champ de filtre, ou
  - `filter_id="mon-tableau"` : lie les champs portant `class="table-filter"`
    `data-filter-id="mon-tableau"`
  - `filter_columns="0,1"` : index 0-based des colonnes filtrées (toutes si absent)

Filtrage — types de champs supportés :

- `input` texte : filtrage temps réel
- `select` : filtrage par option
- groupe de checkboxes : OU entre cases du même groupe
- checkbox unique : cochée = filtre, décochée = tout afficher
- `<tr data-search="valeur1 valeur2">` : données de filtrage invisibles
- plusieurs filtres se combinent en ET

Lignes expandables : `expandable=True` sur la table, puis dans le corps :

```html
<tr>
    {% ui_td %}
    <button type="button" class="toggle-row-btn" data-target="details-row-1"
            aria-label="Détails"><i class="fa-solid fa-chevron-right"></i></button>
    {% end_ui_td %}
    ...
</tr>
<tr id="details-row-1" style="display: none;">
    <td colspan="...">Contenu détaillé</td>
</tr>
```

Le clic bascule l'affichage et pivote l'icône `fa-chevron-right` / `fa-chevron-down`.

---

## Tag / Badge

```html
{% ui_tag text="Actif" color="success" %}
{% ui_tag text="Validé" color="info" icon="fas fa-check" dot=False %}
```

- `text` (requis) ; `color` : couleur Bulma (défaut `"primary"`) ; `dot` : point coloré
  (défaut `True`) ; `icon` ; `css_classes`

---

## Chevron

```html
{% ui_chevron direction="right" %}
{% ui_chevron direction="down" size="small" %}
```

- `direction` : `down`, `right`, `up`, `left` (défaut `down` ; valeur invalide → `down`)
- `size`, `css_classes`

---

## Message

```html
{% ui_message content="Simple message" %}
{% ui_message title="Avertissement" content="Action irréversible" color="warning" %}
{% ui_message_info content="Info" %}
{% ui_message_success content="OK" %}
{% ui_message_warning content="Attention" %}
{% ui_message_danger content="Erreur" %}
{% ui_message content="<strong>HTML de confiance</strong>" is_safe=True %}
```

- `content` (requis) : **échappé par défaut** (`is_safe=False`). `is_safe=True` rend le HTML
  tel quel — uniquement pour du contenu statique ou déjà assaini, jamais une saisie utilisateur
- `color` (défaut `primary`), `title` (toujours échappé), `css_classes`
- kwargs → attributs HTML (`id`, `data-*`...)

---

## Stepper

```python
# views.py — liste de libellés ou de dicts
STEPS = ["Identification", "Question secrète", "Nouveau mot de passe"]
STEPS = [
    {"label": "Salarié", "description": "Identité"},
    {"label": "Coordonnées", "icon": "fas fa-address-card"},
]
```

```html
{% ui_stepper steps current=2 %}
{% ui_stepper steps current=3 completed="1,2" aria_label="Création de compte" css_classes="mb-5" %}
```

- `steps` (requis) : libellés ou dicts `{"label", "description", "icon"}`
- `current` : numéro de l'étape active (à partir de 1)
- `completed` : numéros complétés (liste ou `"1,2"`) ; défaut : les étapes avant `current`
- `aria_label` (défaut `"Progression"`), `css_classes`

Personnalisation CSS via variables sur `.ui-stepper` : `--ui-stepper-size`,
`--ui-stepper-line-color`, `--ui-stepper-active-color`, `--ui-stepper-text-color`.

---

## Indicateurs de défilement pour onglets

```html
<div class="tabs-scroll-wrapper">
    <div class="tabs">...</div>
    {% ui_tabs_scroll_hints %}
</div>
```

Après un swap HTMX, rappeler `loadTabsScrollHints()` côté JS.

---

## Modale de confirmation de soumission

```html
{% load elixir_toolkit_tags %}

<!-- Contenu personnalisé de la modale (optionnel, caché) -->
<div id="my-modal-content" style="display: none;">
    <p>Êtes-vous sûr de vouloir soumettre ce formulaire ?</p>
    <div class="form-summary-container"></div>
</div>

<form id="my-form" method="post" action="...">
    {% csrf_token %}
    ... champs ...
    <button type="button" class="button is-primary js-form-confirm" data-form-confirm="my-form">
        Soumettre
    </button>
</form>

{% ui_form_confirm_submit form_id="my-form" content_id="my-modal-content"
   modal_title="Confirmation de soumission" submit_text="Confirmer"
   cancel_text="Annuler" modal_size="is-medium" %}
```

- `form_id` (requis) : ID du formulaire intercepté
- `content_id` : ID d'un élément contenant le contenu personnalisé de la modale
- `modal_title` (défaut `"Confirmation"`), `submit_text` (défaut `"Envoyer"`),
  `cancel_text` (défaut `"Retour"`), `modal_size` (`is-small`/`is-medium`/`is-large`)
- `summary_container_class` (défaut `"form-summary-container"`) : si une `div` avec cette
  classe existe dans le contenu, une synthèse des champs du formulaire y est injectée

Le bouton de soumission doit être `type="button"` avec la classe `js-form-confirm` ou
l'attribut `data-form-confirm="ID_FORMULAIRE"`.

Comportements : validation HTML5 avant ouverture (champs invalides marqués `is-danger`),
fermeture par fond / ✕ / Escape / bouton Retour, état `is-loading` sur le bouton pendant
l'envoi. API JS : `window.FormConfirmSubmit` (`openModal`, `closeAllModals`,
`highlightInvalidFields`).

---

## CKEditor (librairie `ckeditor_tags`)

```html
{% load ckeditor_tags %}
{% ckeditor_pre upload_url="/ckeditor/upload/" %}   {# AVANT {{ form.media }} #}
{{ form.media }}
{{ form }}
{% ckeditor_post %}                                  {# APRÈS le formulaire #}
```

`ckeditor_post` charge les plugins externes du toolkit (upload adapter, clipboard manager)
et est compatible HTMX.

---

## Captcha LiveIdentity (librairie `liveidentity_tags`)

```html
{% load liveidentity_tags %}
{% render_captcha_script form_id="id-du-formulaire" %}
```

Nécessite `LIVEIDENTITY_SP_KEY` dans les settings. Validation côté serveur :
`validate_liveidentity_token(request)` (cf. `views-mixins.md`).

---

## Filtre `split`

```html
{{ value|split }}
```

Divise une chaîne sur les espaces, renvoie `None` si vide. (Nom trompeur : pas de
séparateur paramétrable.)
