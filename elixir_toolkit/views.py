from django.views.generic import FormView
from django.shortcuts import render


class AsyncFormView(FormView):
    """Ceci est une réécriture async de la ProcessFormView de Django
    pour permettre d'utiliser des vues basées sur des formulaires avec
    des appels asynchrones (ex: httpx).
    Voir le fichier django/views/generic/edit.py pour la version synchrone d'origine."""

    async def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())
    
    async def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return await self.form_valid(form)
        else:
            return self.form_invalid(form)

    async def put(self, *args, **kwargs):
        return self.post(*args, **kwargs)
