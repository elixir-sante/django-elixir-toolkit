from django import shortcuts
from django.utils.deprecation import MiddlewareMixin


class RedirectException(Exception):
    def __init__(self, url):
        self.url = url


class RedirectMiddleware(MiddlewareMixin):
    async_capable = True
    sync_capable = True

    def process_exception(self, request, exception):
        if isinstance(exception, RedirectException):
            return shortcuts.redirect(exception.url)
        return exception


def redirect_now(url):
    raise RedirectException(url)
