# Référence : vues, mixins, middleware et utilitaires

## Mixins de vues (`elixir_toolkit.mixins`)

### Dispatch avec `pre_dispatch`

`MixinDispatch` définit un crochet `pre_dispatch(request, *args, **kwargs)` appelé avant le
dispatch, pour charger les données nécessaires au contexte.

Deux variantes, à choisir selon la vue :

```python
from elixir_toolkit.mixins import AsyncMixinDispatch, SyncMixinDispatch

class MyView(AsyncMixinDispatch, View):        # vues async
    async def pre_dispatch(self, request, *args, **kwargs): ...

class MyView(SyncMixinDispatch, View):         # vues sync
    def pre_dispatch(self, request, *args, **kwargs): ...
```

- `AsyncMixinDispatch` appelle `pre_dispatch` via `sync_to_async` (le `pre_dispatch` peut
  rester synchrone) puis poursuit le dispatch async.
- `SyncMixinDispatch` exige que la vue cible définit `view_is_async` (toute sous-classe de
  `View` l'a) et refuse une vue async avec un message `ImproperlyConfigured`.

### Clé de session obligatoire (async uniquement)

```python
from elixir_toolkit.mixins import AsyncCheckSessionKey

class MyView(AsyncCheckSessionKey, View):
    required_session_key = "insurer_id"   # str ou liste de str
    def get_redirect_url(self) -> str:    # obligatoire
        return reverse("home")
```

Si la/les clés sont absentes de la session (GET et POST), l'utilisateur est redirigé vers
`get_redirect_url()`.

### Titres de page

```python
from elixir_toolkit.mixins import PageTitleMixin

class MyView(PageTitleMixin, TemplateView):
    page_title = "Accueil"
    page_subtitle = "Sous-titre"
```

Injecte `page_title` / `page_subtitle` dans le contexte du template.

### Champs en lecture seule

```python
from elixir_toolkit.mixins import FormReadOnlyFieldMixin

class MyUpdateView(FormReadOnlyFieldMixin, UpdateView):
    fields_readonly = ["created_at", "siren"]
```

Passe les champs listés en `disabled=True`. La liste peut aussi être définie via
`Meta.fields_readonly` sur le formulaire (les deux se cumulent). Fonctionne sur les vues
avec `get_form` (CreateView, UpdateView, FormView...).

### Dépendances entre champs

```python
from elixir_toolkit.mixins import FormDependencyFieldMixin

class MyView(FormDependencyFieldMixin, FormView):
    fields_dependencies = {"is_pro": ["siren", "company_name"]}
```

Pose `data-depends-on="is_pro"` sur les widgets des champs contrôlés ; le JS
`fields-dependencies.js` (chargé par `toolkit_assets`) affiche/masque les champs selon la
valeur du contrôleur. La liste peut aussi venir de `Meta.fields_dependencies` du formulaire.

---

## Middleware (`elixir_toolkit.middleware`)

### Redirection immédiate

```python
from elixir_toolkit.middleware import redirect_now

def my_view(request):
    if not request.user.is_authenticated:
        redirect_now(reverse("login"))   # ne retourne jamais
```

`redirect_now(url)` lève `RedirectException`, interceptée par `RedirectMiddleware`
(sync et async) qui renvoie la redirection HTTP. **`RedirectMiddleware` doit être présent
dans `MIDDLEWARE`.**

### Middleware par activation

```python
from elixir_toolkit.middleware import BaseMiddleware

class MyMiddleware(BaseMiddleware):
    activator = "ma_valeur"   # le middleware ne s'exécute que si getattr(view_class, activator)

    def run(self, request):  # retourne une HttpResponse ou None
        ...
```

Le match de vue est résolu une seule fois par requête et mis en cache sur
`request._resolver_match` (réutilisable par les middlewares suivants).

---

## Utilitaires (`elixir_toolkit.utils`)

### Session (versions sync et async)

```python
from elixir_toolkit.utils import (
    session_get, session_set, session_pop,       # sync
    session_aget, session_aset, session_apop,    # async (wrappées sync_to_async)
)

value = session_get(request, "key", default=None)
session_set(request, insurer_id=42)     # kwargs multiples autorisés, marque la session modifiée
session_pop(request, "key1", "key2")
value = await session_aget(request, "key")
```

### `parse_date(date_str, force_date=False)`

Parseur de dates tolérant (via `dateutil`) : accepte ISO, `19980201`, `1998/02/01`,
`199802011555`, suffixes `Z`/offsets... Renvoie un `datetime` localisé, ou un `date` si
`force_date=True`. Les chaînes sentinelles `99999999` et `00000000` deviennent `9999-12-31`.
Lève `ValueError` si le format n'est pas reconnu.

### Captcha LiveIdentity

```python
from elixir_toolkit.utils import validate_liveidentity_token

async def post(self, request, *args, **kwargs):
    if not await validate_liveidentity_token(request):
        # token POST : request.POST["liveidentity_token"] (extraction centralisée)
        return redirect("login")
```

Settings requis : `LIVEIDENTITY_CLIENT_ID`, `LIVEIDENTITY_SECRET`. Un token absent ou égal
à `"100"` (erreur front) invalide directement. Côté template :
`{% render_captcha_script form_id="..." %}` (cf. `templatetags.md`).

---

## Defaults CKEditor (`elixir_toolkit.defaults`)

Au chargement de l'app, les settings absents sont injectés :

- `CKEDITOR_5_ALLOW_ALL_FILE_TYPES = True`
- `CKEDITOR_5_UPLOAD_FILE_TYPES = ['jpeg', 'pdf', 'jpg', 'png']`
- `CKEDITOR_5_FILE_UPLOAD_PERMISSION = "authenticated"`
- `CKEDITOR_5_CONFIGS` avec les profils :
  - `default` : toolbar vide, FR
  - `extends` : mise en forme complète, tableaux, couleurs, liens internes
    (`linkPickerUrl: /ckeditor/internal-links/`)
  - `custom_page` : + upload d'images/fichiers (plugins externes du toolkit),
    htmlEmbed, MediaEmbed
  - `light` : liste à puces uniquement
  - `description_only` : lecture seule
  - `lightandlink` : puces + liens

Les profils sont utilisables via `CKEditor5Field(config_name="extends")` de
django_ckeditor_5.
