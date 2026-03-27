from django.views.generic import FormView
from test_views.forms import FormExample

class FormTestView(FormView):
    template_name = "form_test.html"
    form_class = FormExample

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        filtres_couleurs = [('red', 'Rouge'), ('green', 'Vert'), ('blue', 'Bleu')]
        filtres_chiffres = [('1', 'Un'), ('2', 'Deux'), ('3', 'Trois')]

        context['mes_filtres'] = [
            filtres_couleurs,
            filtres_chiffres
        ]   
            
        context['mes_options_paiement'] = [
            ('SCHE', 'Paiement échéance'),
            ('FREE', 'Montant libre'),
            ('CANC', 'Annulé'),
        ]
        
        context['objets_test'] = [
            {'color': 'red', 'num': '1', 'name': 'Rouge 1'},
            {'color': 'red', 'num': '2', 'name': 'Rouge 2'},
            {'color': 'blue', 'num': '1', 'name': 'Bleu 1'},
            {'color': 'green', 'num': '3', 'name': 'Vert 3'},
        ]
        
        return context