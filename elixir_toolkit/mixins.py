from asgiref.sync import sync_to_async
from django.core.exceptions import ImproperlyConfigured


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
