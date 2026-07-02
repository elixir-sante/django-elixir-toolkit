from asgiref.sync import sync_to_async
import base64
import logging
from django.conf import settings
from django.http import HttpRequest
import httpx

logger = logging.getLogger(__name__)


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


async def validate_liveidentity_token(request: HttpRequest) -> bool:
    """
    Valide de manière asynchrone le token LiveIdentity extrait de la requête.
    Centralisé dans le toolkit.
    """
    # Extraction centralisée : si le nom du champ change, on le modifie uniquement ici
    token = request.POST.get("liveidentity_token")
    
    if not token or token == "100":
        logger.warning("[LiveIdentity] Validation abandonnée : token manquant ou erreur front (code 100).")
        return False
        
    url = "https://captcha.liveidentity.com/captcha/public/backend/api/v4/captcha/check"
    
    client_id = getattr(settings, 'LIVEIDENTITY_CLIENT_ID', None)
    client_secret = getattr(settings, 'LIVEIDENTITY_SECRET', None)
    
    if not client_id or not client_secret:
        logger.error("[LiveIdentity] Configuration manquante (CLIENT_ID ou SECRET) dans les settings.")
        return False

    # Encodage Basic Auth
    raw_credentials = f"{client_id.strip()}:{client_secret.strip()}"
    base64_credentials = base64.b64encode(raw_credentials.encode('utf-8')).decode('utf-8')
    
    headers = {
        "authorization": f"Basic {base64_credentials}",
        "content-type": "application/json"
    }
    
    payload = {
        "antibotToken": token
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, headers=headers, timeout=5.0)
            if response.status_code == 200:
                result = response.json()
                return result.get("result") == "SUCCESS"
                
            logger.error(f"[LiveIdentity Error {response.status_code}] Réponse Orange : {response.text}")
        except httpx.RequestError as exc:
            logger.error(f"[LiveIdentity Network Error] Échec de la requête : {exc}")
            
    return False