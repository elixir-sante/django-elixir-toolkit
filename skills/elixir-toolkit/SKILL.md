---
name: elixir-toolkit
description: Utilise ce skill à chaque fois que tu écris un template, un formulaire ou une vue Django dans un projet dépendant de django-elixir-toolkit (Elixir Santé). Il documente les composants UI Bulma (ui_button, ui_table, ui_message, ui_select, ui_stepper, etc.), les champs crispy-forms (ToolkitFileField, ToolkitSelectField, FileUpload), les helpers de formulaire, les mixins de vues, le middleware et les validateurs — et ce qu'il faut utiliser au lieu de réécrire du HTML/CSS/JS à la main.
---

# django-elixir-toolkit

Librairie de composants UI pour Django, basée sur **Bulma** et **django-crispy-forms** avec **crispy-bulma**.
Code source de référence : `elixir_toolkit/` dans le dépôt `django-elixir-toolkit`.

## Prérequis du projet hôte

À vérifier avant toute utilisation (une seule fois par projet) :

```python
# settings.py
INSTALLED_APPS = [
    ...
    "crispy_forms",
    "crispy_bulma",
    "elixir_toolkit",
    ...
]
CRISPY_ALLOWED_TEMPLATE_PACKS = "bulma"
CRISPY_TEMPLATE_PACK = "bulma"
```

Dans le template de base :

```html
{% load elixir_toolkit_tags %}
{% toolkit_assets %}
```

`{% toolkit_assets %}` charge déjà Bulma, Font Awesome, Selectize, jQuery et Tablesorter (CDN),
plus tous les CSS/JS du toolkit (date, limite de caractères, confirmation de soumission,
filtres de tableaux, dépendances de champs, etc.).
**Ne jamais ré-inclure ces ressources manuellement** (pas de `<script src=...jquery...>`,
pas de `<link>` Bulma, pas de copie de `max-length.js`).

Paramètre optionnel : `{% toolkit_assets version="1.0.0" %}` fixe la version de Bulma chargée
par CDN (défaut : `1.0.0`).

## Règles d'or

1. **Composant d'abord.** Avant d'écrire du HTML Bulma à la main, vérifier la table de
   correspondance ci-dessous. Si le toolkit le fournit, l'utiliser.
2. **Le Django standard suffit souvent.** Le toolkit patche `forms.DateInput` et
   `forms.CharField` au chargement de l'app :
   - champ date → `forms.DateField(...)` simple, rendu en `<input type="date">` natif,
     valeur ISO, croix de réinitialisation incluse. Ne pas créer de widget custom.
   - limite de caractères → `max_length=400` sur `CharField` / `TextField` / `CKEditor5Field`.
     Compteur, blocage à la frappe et validation serveur sont automatiques.
3. **Formulaires crispy.** Utiliser `CustomFormHelper` ou `SuperFormHelper` du toolkit,
   pas le `FormHelper` de crispy-forms nu.
4. **Champs spécifiques du toolkit** (détails dans `references/forms.md`) :
   - fichier : `ToolkitFileField` (unique) ou `MultipleFileField`, rendus via `FileUpload()`
     dans le `Layout` crispy — le rendu custom casse le comportement du champ.
   - select stylé (Selectize) dans un formulaire crispy : `ToolkitSelectField('champ', icon=...)`.
   - mot de passe : `PasswordWithIconField`.
5. **Sécurité.** `ui_message` échappe le contenu par défaut. Ne passer `is_safe=True` que
   pour du HTML statique de confiance — jamais pour du contenu saisie par l'utilisateur.
6. **Ne pas réimplémenter le JS du toolkit.** Les comportements s'activent par attributs
   `data-*` (`data-max-size`, `data-depends-on`, `data-form-confirm`, `data-search`, ...) ou par
   classes CSS (`js-form-confirm`, `toggle-row-btn`, `table-filter`). Lire
   `references/templatetags.md` avant d'écrire du JS lié à un composant.

## Correspondance besoin → composant

| Besoin | Solution |
|---|---|
| Bouton / lien bouton | `{% ui_button %}`, `{% ui_button_primary %}`, `{% ui_button_secondary %}` |
| Sélecteur stylé (hors formulaire crispy) | `{% ui_select %}` |
| Sélecteur dans un formulaire crispy | `ToolkitSelectField` |
| Barre de filtres | `{% ui_filter_bar %}` |
| Liste d'éléments type Bulma | `{% ui_list %}` |
| Tableau (tri, filtrage, expandable) | `{% ui_table %}` + `{% ui_th %}` / `{% ui_td %}` |
| Badge / statut | `{% ui_tag %}` |
| Chevron / flèche | `{% ui_chevron %}` |
| Message / alerte | `{% ui_message %}` (+ variantes `_info`, `_success`, `_warning`, `_danger`) |
| Parcours en étapes | `{% ui_stepper %}` |
| Indicateurs de défilement d'onglets | `{% ui_tabs_scroll_hints %}` |
| Modale de confirmation de soumission | `{% ui_form_confirm_submit %}` |
| Upload de fichier | `ToolkitFileField` / `MultipleFileField` + `FileUpload()` |
| Champ date | `forms.DateField` standard (auto-patché) |
| Limite de caractères | `max_length=` standard (auto-patché) |
| CKEditor | `{% ckeditor_pre %}` / `{% ckeditor_post %}` (librairie `ckeditor_tags`) |
| Captcha LiveIdentity | `{% render_captcha_script %}` (librairie `liveidentity_tags`) + `validate_liveidentity_token` |

## Pièges courants

- `ui_table`, `ui_th`, `ui_td` sont des **tags à bloc** : `{% ui_table %}...{% end_ui_table %}`,
  `{% ui_th %}Titre{% end_ui_th %}`.
- Tri de tableau : `orderable=True` sur `{% ui_table %}` active le tri (Tablesorter) ;
  `{% ui_th orderable=False %}` exclut une colonne du tri.
- Filtrage de tableau : `filterable=True` + `filter_target="#id-du-champ"` ou
  `filter_id="mon-tableau"` avec `<input class="table-filter" data-filter-id="mon-tableau">`.
  jQuery et `table-filter.js` sont déjà chargés par `{% toolkit_assets %}` — ne pas ajouter
  de `<script>` manuel.
- `ui_select` attend `options=[(valeur, libellé), ...]` (ou un dict, ou une chaîne littérale).
- CKEditor : `{% ckeditor_pre %}` **avant** `{{ form.media }}`, `{% ckeditor_post %}` **après**
  le rendu du formulaire. Pour brancher du code sur un éditeur, utiliser
  `window.elixirOnCkeditorReady(function (editor) {...})` — pas `ckeditorRegisterCallback`
  (déjà réservé par le toolkit).
- `redirect_now(url)` lève une exception interceptée par `RedirectMiddleware` : ce middleware
  doit être dans `MIDDLEWARE`.
- Les mixins `AsyncCheckSessionKey` et `redirect_now` sont pour des vues **async** ;
  `SyncMixinDispatch` refuse les vues async.
- `CustomFormHelper` rend `form_tag = False` : le formulaire crispy n'écrit pas la balise
  `<form>`, à écrire dans le template.

## Références détaillées

Lire au moment où le besoin apparaît, pas avant :

- `references/templatetags.md` — tous les tags de template : signatures complètes, paramètres,
  défauts, exemples, comportement JS associé.
- `references/forms.md` — champs de formulaire, helpers crispy, validateurs, patchs
  automatiques (date, max_length), intégration CKEditor.
- `references/views-mixins.md` — mixins de vues, middleware, utilitaires session/date,
  captcha LiveIdentity, profils CKEditor par défaut.
