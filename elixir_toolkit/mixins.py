import logging
from asgiref.sync import sync_to_async
from django.contrib import messages
from django.core.exceptions import ImproperlyConfigured
from elixir_toolkit.utils import session_aget
from elixir_toolkit.middleware import redirect_now

logger = logging.getLogger(__name__)
class MixinDispatch:
    """
    Mixin to ensure that the pre_dispatch method is called before the main dispatch method.
    This allows us to load necessary data for the context before handling the request.
    """
    def pre_dispatch(self, request, *args, **kwargs):
        """Méthode appelée avant le dispatch pour charger les données nécessaires au contexte."""
        pass


class AsyncMixinDispatch:

    async def dispatch(self, request, *args, **kwargs):
        await sync_to_async(self.pre_dispatch)(request, *args, **kwargs) # type: ignore
        return await super().dispatch(request, *args, **kwargs) # type: ignore


class SyncMixinDispatch:

    def dispatch(self, request, *args, **kwargs):
        if not hasattr(self, 'view_is_async'):
            raise ImproperlyConfigured(
                f"{self.__class__.__qualname__} is missing the 'view_is_async' class property. "
                "This is defined by standard View class. "
                "Your mixin needs to be used with a View subclass."
            )
        if self.view_is_async:  # type: ignore
            raise ImproperlyConfigured(
                f"{self.__class__.__qualname__} is used in a synchronous context but is async! "
                "Use AsyncMixinDispatch instead of SyncMixinDispatch."
            )
        self.pre_dispatch(request, *args, **kwargs) # type: ignore
        return super().dispatch(request, *args, **kwargs) # type: ignore


class AsyncCheckSessionKey:
    """
    Checks if the required session key is present in the session,
    before GET and POST requests.
    If not, redirect to the URL returned by get_redirect_url().
    This one is for async views.
    """
    required_session_key = None

    def get_redirect_url(self) -> str:
        raise ImproperlyConfigured('This should be overriden by your class')

    async def _check_keys_presence_or_redirect(self, keys):
        if type(keys) is str:
            keys = [keys]
        for key in keys:
            if not await session_aget(self.request, key):
                logger.error(f'Missing {key} in session, redirecting user')
                redirect_now(self.get_redirect_url())

    async def post(self, request, *args, **kwargs):
        if not self.required_session_key:
            raise ImproperlyConfigured('If this mixin is used, you should add \'required_session_key\' (str or list)')
        await self._check_keys_presence_or_redirect(self.required_session_key)
        return await super().post(request, *args, **kwargs)

    async def get(self, request, *args, **kwargs):
        if not self.required_session_key:
            raise ImproperlyConfigured('If this mixin is used, you should add \'required_session_key\' (str or list)')
        await self._check_keys_presence_or_redirect(self.required_session_key)
        return await super().get(request, *args, **kwargs)
    
    
class ConfigPageMixin(object):
    success_message = "Paramètres mis à jour."
    page_title = ""
    page_subtitle = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self, "page_title"):
            context["page_title"] = self.page_title
        if hasattr(self, "page_subtitle"):
            context["page_subtitle"] = self.page_subtitle
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if not form:
            return form

        self._apply_readonly_fields(form)
        self._apply_fields_dependencies(form)

        return form

    def _apply_readonly_fields(self, form):
        """Désactive les champs marqués comme readonly dans la vue ou le formulaire."""
        # Extraction depuis la vue
        readonly_fields = list(getattr(self, "fields_readonly", []))
        
        # Extraction depuis la Meta du formulaire
        meta = getattr(form, "Meta", None)
        if meta and hasattr(meta, "fields_readonly"):
            readonly_fields.extend(meta.fields_readonly)

        # Application
        for field in readonly_fields:
            if field in form.fields:
                form.fields[field].disabled = True

    def _apply_fields_dependencies(self, form):
        """Ajoute les attributs de dépendances de données aux widgets des champs concernés."""
        # Récupération des dépendances (Vue prioritaire sur Meta)
        meta = getattr(form, "Meta", None)
        dependencies = getattr(self, "fields_dependencies", None) or getattr(meta, "fields_dependencies", None)

        if not dependencies:
            return

        # Application des attributs HTML5 data-*
        for controller, controlled_fields in dependencies.items():
            for field in controlled_fields:
                if field in form.fields:
                    form.fields[field].widget.attrs['data-depends-on'] = controller

    def get_object(self):
        return self.organization.insurer

    def get_success_url(self):
        if self.success_url:
            return self.get_organization_url(self.success_url)
        return super().get_success_url()

    def form_valid(self, form):
        redirect = super().form_valid(form)
        messages.success(self.request, self.success_message)
        return redirect

