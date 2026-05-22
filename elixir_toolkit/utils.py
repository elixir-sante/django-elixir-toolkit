from asgiref.sync import sync_to_async

__all__ = [
    "session_get",
    "session_aget",
    "session_set",
    "session_aset",
    "session_pop",
    "session_apop",
]


@sync_to_async
def session_aget(request, key, default=None):
    return request.session.get(key, default)

def session_get(request, key, default=None):
    return request.session.get(key, default)

@sync_to_async
def session_aset(request, **kwargs):
    for k, v in kwargs.items():
        request.session[k] = v
    request.session.modified = True

def session_set(request, **kwargs):
    for k, v in kwargs.items():
        request.session[k] = v
    request.session.modified = True

@sync_to_async
def session_apop(request, *keys):
    for k in keys:
        request.session.pop(k, None)
    request.session.modified = True

def session_pop(request, *keys):
    for k in keys:
        request.session.pop(k, None)
    request.session.modified = True