from django.shortcuts import render
from django.views.generic import FormView

from test_views.forms import FormExample


# class HomeTestView(TemplateView):
#     template_name = "home.html"



class FormTestView(FormView):
    template_name = "form_test.html"
    form_class = FormExample

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mes_filtres_couleurs'] = [
            ('red', 'Rouge'),
            ('green', 'Vert'),
            ('blue', 'Bleu'),
        ]
        context['mes_options_paiement'] = [
            ('SCHE', 'Paiement échéance'),
            ('FREE', 'Montant libre'),
            ('CANC', 'Annulé'),
        ]
        
        # Tu peux même envoyer une valeur sélectionnée par défaut
        context['mode_par_defaut'] = 'SCHE'
        
        return context