from asgiref.sync import sync_to_async

@sync_to_async
def _session_aget(request, key, default=None):   # utils.py to put in toolkit, dans le commit : ajouter self.context = self.self.get_context_data() dans view dans toolkit aussi
    return request.session.get(key, default)

def _session_get(request, key, default=None):
    return request.session.get(key, default)

@sync_to_async
def _session_aset(request, **kwargs):
    for k, v in kwargs.items():
        request.session[k] = v

def _session_set(request, **kwargs):
    for k, v in kwargs.items():
        request.session[k] = v

@sync_to_async
def _session_apop(request, *keys):
    for k in keys:
        request.session.pop(k, None)

def _session_pop(request, *keys):
    for k in keys:
        request.session.pop(k, None)