from asgiref.sync import sync_to_async

@sync_to_async
def session_aget(request, key, default=None):   # utils.py to put in toolkit, dans le commit : ajouter self.context = self.self.get_context_data() dans view dans toolkit aussi
    return request.session.get(key, default)

def session_get(request, key, default=None):
    return request.session.get(key, default)

@sync_to_async
def session_aset(request, **kwargs):
    for k, v in kwargs.items():
        request.session[k] = v

def session_set(request, **kwargs):
    for k, v in kwargs.items():
        request.session[k] = v

@sync_to_async
def session_apop(request, *keys):
    for k in keys:
        request.session.pop(k, None)

def session_pop(request, *keys):
    for k in keys:
        request.session.pop(k, None)