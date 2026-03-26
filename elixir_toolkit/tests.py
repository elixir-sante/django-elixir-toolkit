from django.test import TestCase
from django.template import Context, Template

class ToolkitButtonsTest(TestCase):
    def render_template(self, string, context=None):
        context = context or {}
        context = Context(context)
        return Template(string).render(context)

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
        
        self.assertIn('class="button is-primary"', rendered)

    def test_attribute_transformation(self):
        """Vérifie que l'underscore devient un tiret (data_id -> data-id)"""
        template = "{% load elixir_toolkit_tags %}{% ui_button text='Outil' data_id='123' %}"
        rendered = self.render_template(template)
        
        # On vérifie la présence de l'attribut transformé par flatatt
        self.assertIn('data-id="123"', rendered)
        self.assertNotIn('data_id', rendered)

    def test_icon_rendering(self):
        """Vérifie que l'icône est présente si demandée"""
        template = "{% load elixir_toolkit_tags %}{% ui_button text='Email' icon='fas fa-envelope' %}"
        rendered = self.render_template(template)
        
        self.assertIn('<i class="fas fa-envelope"></i>', rendered)
        self.assertIn('<span class="icon">', rendered)
        

class ToolkitFilterBarTest(TestCase):
    def render_template(self, string, context=None):
        context = Context(context or {})
        return Template(string).render(context)

    def test_filter_bar_basic_render(self):
        filters = [('active', 'Actifs'), ('closed', 'Fermés')]
        template = "{% load elixir_toolkit_tags %}{% ui_filter_bar filters=filters %}"
        rendered = self.render_template(template, {'filters': filters})
        
        self.assertIn('Tout', rendered)
        self.assertIn('data-filter="active"', rendered)
        self.assertIn('Actifs', rendered)
        self.assertIn('data-filter="closed"', rendered)
        self.assertIn('Fermés', rendered)

    def test_filter_bar_identifier(self):
        filters = [('1', 'Un')]
        template = "{% load elixir_toolkit_tags %}{% ui_filter_bar filters=filters identifier='projects' %}"
        rendered = self.render_template(template, {'filters': filters})
        
        # Vérifie l'ID du div
        self.assertIn('id="filter-bar-projects"', rendered)
        self.assertIn("getElementById('filter-bar-projects')", rendered)
        self.assertIn("identifier: 'projects'", rendered)

    def test_filter_bar_default_identifier(self):
        filters = []
        template = "{% load elixir_toolkit_tags %}{% ui_filter_bar filters=filters %}"
        rendered = self.render_template(template, {'filters': filters})
        
        self.assertIn('id="filter-bar-default"', rendered)