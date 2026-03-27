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
        context['remboursements_test'] = [
            {
                'id': 1,
                'libelle': 'Consultation Médecin Généraliste',
                'date_info': 'Remboursé le 12/03/2024',
                'montant': '25,00 €',
                'patient': 'Jean Dupont',
                'user_icon': 'user',
                'type_icon': 'hand-holding-medical'
            },
            {
                'id': 2,
                'libelle': 'Pharmacie - Achat médicaments',
                'date_info': 'Remboursé le 10/03/2024',
                'montant': '12,40 €',
                'patient': 'Marie Dupont',
                'user_icon': 'user-female', # si tu gères des icônes différentes
                'type_icon': 'pills'
            },
            {
                'id': 3,
                'libelle': 'Analyse de sang',
                'date_info': 'Acte du 05/03/2024',
                'montant': '45,00 €',
                'patient': 'Jean Dupont',
                'user_icon': 'user',
                'type_icon': 'flask'
            }
        ]
        
        return context