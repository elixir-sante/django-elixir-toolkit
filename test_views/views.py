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
        context['donnees_inventaire'] = [
            {
                'nom': 'MacBook Pro M3',
                'sku': 'APP-MBP-2024',
                'categorie': 'Hardware',
                'prix': 2499.00,
                'stock': 12,
                'icon_item': 'laptop'
            },
            {
                'nom': 'Licence PyCharm',
                'sku': 'SOFT-JB-001',
                'categorie': 'Software',
                'prix': 199.00,
                'stock': 50,
                'icon_item': 'code'
            }
        ]

        # 2. La configuration des colonnes (L'ordre compte !)
        context['config_colonnes'] = [
            {
                'header': 'Produit', 
                'field': 'nom', 
                'sub_field': 'sku',     # Affiche le SKU sous le nom
                'icon_field': 'icon_item' # Icône dynamique par ligne
            },
            {
                'header': 'Catégorie', 
                'field': 'categorie', 
                'type': 'badge'         # Rendu sous forme de tag Bulma
            },
            {
                'header': 'Prix Unit.', 
                'field': 'prix', 
                'type': 'price', 
                'class': 'has-text-weight-bold'
            },
            {
                'header': 'Quantité', 
                'field': 'stock', 
                'suffix': ' unités'     # Ajoute un suffixe personnalisé
            }
        ]
        
        return context