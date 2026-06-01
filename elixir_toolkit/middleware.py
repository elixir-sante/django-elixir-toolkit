class Redirect(Exception):
    def __init__(self, url):
        self.url = url


def redirect_now(url):
    raise Redirect(url)
