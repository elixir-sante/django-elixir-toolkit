import random
from datetime import date, timedelta

from django.views.generic import FormView, TemplateView
from django.contrib import messages
from test_views.forms import (
    FormExample, TableFilterLargeForm, LARGE_TABLE_FILTER_CLASS,
    TYPE_ACTE_CHOICES, VILLE_CHOICES, STATUT_CHOICES,
)

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
            
        context['etapes_simples'] = ["Identité", "Coordonnées", "Paiement", "Confirmation"]

        context['etapes_simples_6'] = ["Compte", "Compte", "Compte", "Compte", "Compte", "Compte"]

        context['etapes_detaillees'] = [
            {'label': 'Compte', 'description': 'Email et mot de passe', 'icon': 'fas fa-user'},
            {'label': 'Profil', 'description': 'Informations personnelles', 'icon': 'fas fa-id-card'},
            {'label': 'Documents', 'description': 'Pièces justificatives', 'icon': 'fas fa-file-upload'},
            {'label': 'Validation', 'description': 'Vérification finale', 'icon': 'fas fa-check-double'},
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
            },
            {
                'nom': 'iPhone 15 Pro',
                'sku': 'APP-IPH-2024',
                'categorie': 'Hardware',
                'prix': 1299.00,
                'stock': 25,
                'icon_item': 'mobile-alt'
            },
            {
                'nom': 'Écran UltraHD 27"',
                'sku': 'DELL-U27-4K',
                'categorie': 'Hardware',
                'prix': 649.00,
                'stock': 8,
                'icon_item': 'desktop'
            },
            {
                'nom': 'Clavier mécanique RGB',
                'sku': 'KB-RAZ-001',
                'categorie': 'Hardware',
                'prix': 149.99,
                'stock': 30,
                'icon_item': 'keyboard'
            },
            {
                'nom': 'Souris gaming',
                'sku': 'MS-LOG-002',
                'categorie': 'Hardware',
                'prix': 79.99,
                'stock': 45,
                'icon_item': 'mouse'
            },
            {
                'nom': 'Casque audio Bluetooth',
                'sku': 'AUD-SON-003',
                'categorie': 'Hardware',
                'prix': 179.99,
                'stock': 15,
                'icon_item': 'headphones'
            },
            
        ]
        
        return context


class TableFilterExampleView(TemplateView):
    template_name = "table_filter_example.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Données pour l'exemple de filtrage
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
            },
            {
                'nom': 'Souris Gaming',
                'sku': 'ACCESS-MOUSE-001',
                'categorie': 'Accessoire',
                'prix': 89.99,
                'stock': 35,
                'icon_item': 'mouse'
            },
            {
                'nom': 'Clavier Mécanique',
                'sku': 'ACCESS-KEYB-002',
                'categorie': 'Accessoire',
                'prix': 129.50,
                'stock': 20,
                'icon_item': 'keyboard'
            },
            {
                'nom': 'Écran 27"',
                'sku': 'MON-27-4K',
                'categorie': 'Hardware',
                'prix': 599.00,
                'stock': 8,
                'icon_item': 'desktop'
            }
        ]
        
        return context


class TableFilterLargeView(TemplateView):
    template_name = "table_filter_large.html"
    nb_lignes = 2000

    def get_lignes(self):
        # Graine fixe : mêmes données à chaque chargement
        rng = random.Random(42)
        prenoms = ['Jean', 'Marie', 'Pierre', 'Sophie', 'Luc', 'Camille', 'Nicolas', 'Julie', 'Thomas', 'Emma', 'Hugo', 'Léa']
        noms = ['Dupont', 'Martin', 'Bernard', 'Petit', 'Durand', 'Leroy', 'Moreau', 'Simon', 'Laurent', 'Lefèvre', 'Michel', 'Garcia']
        types_acte = [value for value, _ in TYPE_ACTE_CHOICES]
        villes = [value for value, _ in VILLE_CHOICES]
        statuts = [value for value, _ in STATUT_CHOICES]
        couleurs_statut = {'Payé': 'success', 'En attente': 'warning', 'Refusé': 'danger'}
        debut = date(2024, 1, 1)

        lignes = []
        for i in range(1, self.nb_lignes + 1):
            statut = rng.choice(statuts)
            montant = round(rng.uniform(5, 1500), 2)
            taux = rng.choice([60, 70, 80, 100])
            lignes.append({
                'id': i,
                'reference': f"REF-{i:05d}",
                'beneficiaire': f"{rng.choice(prenoms)} {rng.choice(noms)}",
                'type_acte': rng.choice(types_acte),
                'ville': rng.choice(villes),
                'statut': statut,
                'couleur_statut': couleurs_statut[statut],
                'montant': montant,
                'taux': taux,
                'rembourse': round(montant * taux / 100, 2) if statut == 'Payé' else 0,
                'date_acte': debut + timedelta(days=rng.randint(0, 600)),
                'tiers_payant': rng.random() < 0.3,
                'praticien': f"Dr {rng.choice(noms)}",
            })
        return lignes

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = TableFilterLargeForm()
        context['filter_target'] = f".{LARGE_TABLE_FILTER_CLASS}"
        context['lignes'] = self.get_lignes()
        return context


class FormConfirmSubmitTestView(TemplateView):
    template_name = "form_confirm_submit_test.html"
    
    def post(self, request, *args, **kwargs):
        messages.success(request, "Formulaire soumis avec succès !")
        return self.render_to_response(self.get_context_data())


class MessageTestView(TemplateView):
    template_name = "message_test.html"
