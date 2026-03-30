# django-elixir-toolkit
Django Toolkit lib by Elixir

### Trucs à réfléchir : 

- Crispy?
- Django-bulma? ou on gère manuellement
- Tests auto
- Comment "publier" la lib

### Import global
- [] Custom_tag pour charger les CSS (Bulma) + JS (Jquery, Selectize)

### Composants
- [] Boutons primaires
- [] Boutons primaires avec icon (FA)
- [] Boutons secondaires avec icon (FA)
- [] Filtres de listes

### Eléments de formulaire
- [] Input
- [] Select
- [] ...




# 🛡️ Django Elixir Toolkit

**Django Elixir Toolkit** est une bibliothèque de composants UI réutilisables pour Django, basée sur le framework CSS **Bulma** et optimisée pour **Django Crispy Forms**.

---

## 🚀 Installation & Import

### 1. Installation via pip
Le toolkit peut être installé directement depuis GitHub. 

* **Production (Choix de la version) :**
```bash
  pip install git+[https://github.com/ton-pseudo/django-elixir-toolkit.git@vX.X.X]
```

* **Développement (Dernières nouveautés) :**
```bash
pip install git+[https://github.com/ton-pseudo/django-elixir-toolkit.git@dev]
```

* **2. Configuration Django**
Ajoute les applications nécessaires dans ton settings.py :

Python
INSTALLED_APPS = [
    ...
    'crispy_forms',
    'crispy_bulma',
    'elixir_toolkit',
    ...
]

CRISPY_ALLOWED_TEMPLATE_PACKS = "bulma"
CRISPY_TEMPLATE_PACK = "bulma"

* **Structure du Projet**
elixir_toolkit/forms.py : Logique des champs file upload.

elixir_toolkit/templatetags/elixir_toolkit_tag.py : les custom_tag a appeller dans les templates pour utiliser les composants

elixir_toolkit/templates/ : Fichiers HTML des composants (organisés par dossiers fields, components).

elixir_toolkit/static/ : Fichiers CSS (button.css, selectize.css).

test_app/ : Projet de test interne servant d'exemple d'implémentation et de sandbox


Pour l'appel des custom_tags : {% ui_button text="Voir la doc" href="https://bulma.io" target="_blank" icon="fas fa-book" %}
Regarder les customs_tags pour voir les paramètres à passer  comme le text. 

Voir les exemples dans l'app test_app pour accéders aux différents exemples d'utilisation des composants/crispy.