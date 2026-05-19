from django.test import TestCase
from django.template import Context, Template
from django import forms

class ToolkitBaseTest(TestCase):
    """Classe de base pour partager la logique de rendu des templates."""
    def render_template(self, string, context=None):
        context = Context(context or {})
        return Template(string).render(context)

class ToolkitButtonsTest(ToolkitBaseTest):
    def test_ui_button_basic_render(self):
        """Vérifie qu'un bouton simple a les bonnes classes et le texte"""
        template = "{% load elixir_toolkit_tags %}{% ui_button text='Mon Bouton' %}"
        rendered = self.render_template(template)
        
        self.assertIn('class="button "', rendered)
        self.assertIn('<span>Mon Bouton</span>', rendered)

    def test_ui_button_primary_inheritance(self):
        """Vérifie que ui_button_primary ajoute bien 'is-primary'"""
        template = "{% load elixir_toolkit_tags %}{% ui_button_primary text='Valider' %}"
        rendered = self.render_template(template)
        
        self.assertIn('is-primary', rendered)

    def test_attribute_transformation(self):
        """Vérifie que l'underscore devient un tiret (data_id -> data-id)"""
        template = "{% load elixir_toolkit_tags %}{% ui_button text='Outil' data_id='123' %}"
        rendered = self.render_template(template)
        
        self.assertIn('data-id="123"', rendered)
        self.assertNotIn('data_id', rendered)

    def test_icon_rendering(self):
        """Vérifie que l'icône est présente si demandée"""
        template = "{% load elixir_toolkit_tags %}{% ui_button text='Email' icon='fas fa-envelope' %}"
        rendered = self.render_template(template)
        
        self.assertIn('<i class="fas fa-envelope"></i>', rendered)
        self.assertIn('<span class="icon">', rendered)


class ToolkitValidationTest(ToolkitBaseTest):
    def test_file_input_error_bulma_styling(self):
        class MockForm(forms.Form):
            file_field = forms.FileField(label="CV", help_text="PDF uniquement", required=True)

        form = MockForm(data={})
        field = form['file_field']
        
        template = '{% include "elixir_toolkit/components/fields/file_input.html" with field=field %}'
        rendered = self.render_template(template, {'field': field})

        self.assertIn('is-danger', rendered)
        self.assertIn('class="help is-danger"', rendered)
        self.assertIn(field.errors[0], rendered) 
        self.assertIn('PDF uniquement', rendered)

    def test_ui_select_manual_options(self):
        template = """
            {% load elixir_toolkit_tags %}
            {% ui_select name="test" options="[('A', 'Alpha'), ('B', 'Beta')]" selected="A" %}
        """
        rendered = self.render_template(template)
        
        self.assertIn('value="A"', rendered)
        self.assertIn('selected', rendered)
        self.assertIn('Alpha', rendered)


class ToolkitSelectizeTest(ToolkitBaseTest):
    def test_ui_select_tag_parsing(self):
        """Vérifie que le tag ui_select transforme bien une string d'options en HTML"""
        template = """
            {% load elixir_toolkit_tags %}
            {% ui_select name="color" options="[('red', 'Rouge'), ('blue', 'Bleu')]" selected="red" %}
        """
        rendered = self.render_template(template)
        
        self.assertIn('id="id_color"', rendered)
        self.assertIn('value="red"', rendered)
        self.assertIn('selected', rendered)
        # CORRECTION : On cherche la classe sans le préfixe 'class=' pour éviter les erreurs d'espaces
        self.assertIn('selectize-control', rendered)

    def test_ui_select_form_integration(self):
        """Vérifie le rendu du select lorsqu'il est lié à un champ Django"""
        class MockSelectForm(forms.Form):
            choice = forms.ChoiceField(
                choices=[('A', 'Option A')],
                help_text="Besoin d'aide ?",
                required=True
            )

        form = MockSelectForm(data={})
        field = form['choice']
        
        template = '{% include "elixir_toolkit/components/select.html" with field=field name="choice" element_id="id_choice" %}'
        rendered = self.render_template(template, {'field': field})

        self.assertIn("Besoin d'aide ?", rendered)

    def test_ui_select_icon_rendering(self):
        """Vérifie que l'icône Bulma est bien injectée dans le select"""
        template = """
            {% load elixir_toolkit_tags %}
            {% ui_select name="test" options="[]" icon="fa-user" %}
        """
        rendered = self.render_template(template)
        
        self.assertIn('has-icons-left', rendered)
        self.assertIn('fa-user', rendered)
        

class ToolkitFilterBarTest(ToolkitBaseTest):
    def test_filter_bar_basic_render(self):
        filters = [('active', 'Actifs'), ('closed', 'Fermés')]
        template = "{% load elixir_toolkit_tags %}{% ui_filter_bar filters=filters %}"
        rendered = self.render_template(template, {'filters': filters})
        
        self.assertIn('Tout', rendered)
        self.assertIn('data-filter="active"', rendered)
        self.assertIn('Actifs', rendered)

    def test_filter_bar_identifier(self):
        filters = [('1', 'Un')]
        template = "{% load elixir_toolkit_tags %}{% ui_filter_bar filters=filters identifier='projects' %}"
        rendered = self.render_template(template, {'filters': filters})
        
        self.assertIn('id="filter-system-projects"', rendered)
        self.assertIn("getElementById('filter-system-projects')", rendered)
        self.assertIn("identifier: 'projects'", rendered)

    def test_filter_bar_default_identifier(self):
        filters = []
        template = "{% load elixir_toolkit_tags %}{% ui_filter_bar filters=filters %}"
        rendered = self.render_template(template, {'filters': filters})
        
        self.assertIn('id="filter-system-default"', rendered)

    def test_filter_bar_simple_list_normalization(self):
        """Vérifie la conversion d'une liste simple en data-group=0"""
        filters = [('red', 'Rouge')]
        template = "{% load elixir_toolkit_tags %}{% ui_filter_bar filters=filters %}"
        rendered = self.render_template(template, {'filters': filters})
        
        self.assertIn('data-filter="red"', rendered)
        self.assertIn('data-group="0"', rendered)

    def test_filter_bar_multi_list_rendering(self):
        """Vérifie la gestion des groupes multiples (listes de listes)"""
        multi_filters = [
            [('red', 'Rouge')],
            [('small', 'Petit')]
        ]
        template = "{% load elixir_toolkit_tags %}{% ui_filter_bar filters=filters identifier='multi' %}"
        rendered = self.render_template(template, {'filters': multi_filters})

        self.assertIn('data-filter="red"', rendered)
        self.assertIn('data-group="0"', rendered)
        self.assertIn('data-filter="small"', rendered)
        self.assertIn('data-group="1"', rendered)

    def test_filter_bar_empty_list(self):
        """Vérifie que le composant reste stable si vide"""
        template = "{% load elixir_toolkit_tags %}{% ui_filter_bar filters=filters %}"
        rendered = self.render_template(template, {'filters': []})
        
        self.assertIn('Tout', rendered)
        self.assertNotIn('data-group="0"', rendered)
        

class ToolkitListTest(ToolkitBaseTest):
    def test_ui_list_basic_rendering(self):
        """Vérifie que la liste affiche le titre, la description et l'extra"""
        items = [{
            'id': 10,
            'name': 'Consultation',
            'info': '12/03/2024',
            'price': '25€'
        }]
        # On précise bien les noms de champs correspondants au dictionnaire
        template = "{% load elixir_toolkit_tags %}{% ui_list items=items title_field='name' desc_field='info' extra_field='price' %}"
        rendered = self.render_template(template, {'items': items})
        
        self.assertIn('Consultation', rendered)
        self.assertIn('12/03/2024', rendered)
        self.assertIn('25€', rendered)
        self.assertIn('fa-angle-right', rendered)

    def test_ui_list_tag_and_icon(self):
        """Vérifie le rendu du badge (tag) et de l'icône principale"""
        items = [{
            'name': 'Test',
            'patient': 'Jean Dupont',
            'type': 'pills'
        }]
        template = """
            {% load elixir_toolkit_tags %}
            {% ui_list items=items title_field='name' tag_label_field='patient' icon_field='type' %}
        """
        rendered = self.render_template(template, {'items': items})
        
        self.assertIn('Jean Dupont', rendered)
        self.assertIn('fa-pills', rendered)
        self.assertIn('tag is-primary', rendered)

    def test_ui_list_clickable_logic(self):
        """Vérifie la présence du container cliquable et du lien par défaut"""
        items = [{'id': 1, 'name': 'Lien Test'}]
        template = "{% load elixir_toolkit_tags %}{% ui_list items=items title_field='name' %}"
        rendered = self.render_template(template, {'items': items})
        
        # Vérifie que href="#" est généré quand link_url_name est absent
        self.assertIn('href="#"', rendered)
        self.assertIn('is-clickable-container', rendered)
        self.assertIn('item-main-link', rendered)

    def test_ui_list_empty_state(self):
        """Vérifie le message si la liste est vide"""
        template = "{% load elixir_toolkit_tags %}{% ui_list items=items %}"
        rendered = self.render_template(template, {'items': []})
        
        self.assertIn('Aucun élément à afficher', rendered)
        

class ToolkitTableTest(ToolkitBaseTest):
    def test_ui_table_multi_purpose(self):
        """Vérifie que le tableau gère les badges, les prix et les suffixes"""
        items = [{'name': 'Test', 'status': 'OK', 'score': 95}]
        cols = [
            {'header': 'Nom', 'field': 'name'},
            {'header': 'Etat', 'field': 'status', 'type': 'badge'},
            {'header': 'Points', 'field': 'score', 'suffix': ' pts'}
        ]
        template = "{% load elixir_toolkit_tags %}{% ui_table items=items columns=cols %}"
        rendered = self.render_template(template, {'items': items, 'cols': cols})
        
        # Vérifie le badge
        self.assertIn('tag is-primary is-light', rendered)
        self.assertIn('OK', rendered)
        # Vérifie le suffixe
        self.assertIn('95 pts', rendered)