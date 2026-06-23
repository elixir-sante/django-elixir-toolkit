from django import shortcuts
from django.utils.deprecation import MiddlewareMixin
from django.urls import resolve
from django.http import HttpResponse


class BaseMiddleware:
    activator = None

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if not self.activator:
            raise NotImplementedError("activator must be defined in a BaseMiddleware subclass")

        match = self.get_resolver_match(request)
        view_class = getattr(match.func, "view_class", None)

        # This will allow us to use Mixin on Middleware (ex: Access Mixin, access self.request)
        self.store_request_in_middleware(request)

        if getattr(view_class, self.activator, False):
            run_result = self.run(request)
            if run_result:
                return run_result

        return self.get_response(request)

    def store_request_in_middleware(self, request):
        if not hasattr(self, "request"):
            self.request = request

    def get_resolver_match(self, request):
        """
        Get the resolver match for the current request.
        This allows to execute resolve() only one time per request,
        and use the result in all next middlewares,
        instead of executing resolve() in each middleware.
        """

        if not hasattr(request, "_resolver_match"):
            request._resolver_match = resolve(request.path_info)
        return request._resolver_match

    def run(self, request) -> None | HttpResponse:
        raise NotImplementedError("run must be defined in a BaseMiddleware subclass")


class RedirectException(Exception):
    def __init__(self, url):
        self.url = url


class RedirectMiddleware(MiddlewareMixin):
    async_capable = True
    sync_capable = True

    def process_exception(self, request, exception):
        if isinstance(exception, RedirectException):
            return shortcuts.redirect(exception.url)
        return None


def redirect_now(url):
    raise RedirectException(url)
