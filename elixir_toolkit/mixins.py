from asgiref.sync import sync_to_async
from django.core.exceptions import ImproperlyConfigured
from elixir_toolkit.utils import session_aget

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
