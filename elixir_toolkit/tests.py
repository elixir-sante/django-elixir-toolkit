from datetime import date

from django.test import TestCase
from django.template import Context, Template
from django import forms

from elixir_toolkit.forms import limit_length
from elixir_toolkit.mixins import FormMaxLengthFieldMixin

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
    def test_ui_table_structure_and_tags(self):
        """Vérifie que le nouveau ui_table génère bien le conteneur Bulma et intègre les sous-composants"""
        template = """
            {% load elixir_toolkit_tags %}
            {% ui_table css_classes="is-striped" %}
                <thead>
                    <tr><th>Nom</th><th>Statut</th></tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Test</td>
                        <td>{% ui_tag text="OK" color="success" %}</td>
                    </tr>
                </tbody>
            {% end_ui_table %}
        """
        rendered = self.render_template(template)
        
        # Vérifie la présence du conteneur responsive et des classes Bulma
        self.assertIn('class="table-container"', rendered)
        self.assertIn('class="table is-fullwidth is-hoverable is-striped"', rendered)
        # Vérifie que le sous-composant tag s'est bien rendu à l'intérieur
        self.assertIn('tag is-success is-light', rendered)
        self.assertIn('OK', rendered)

    def test_ui_table_filterable_basic(self):
        """Vérifie que le ui_table avec filtrage génère les bons attributs data"""
        template = """
            {% load elixir_toolkit_tags %}
            {% ui_table css_classes="is-striped" filterable=True %}
                <thead>
                    <tr><th>Nom</th><th>Statut</th></tr>
                </thead>
                <tbody>
                    <tr><td>Test</td><td>OK</td></tr>
                </tbody>
            {% end_ui_table %}
        """
        rendered = self.render_template(template)
        
        # Vérifie la présence des attributs de filtrage
        self.assertIn('data-filterable="true"', rendered)
        self.assertIn('class="table-container"', rendered)

    def test_ui_table_filterable_with_columns(self):
        """Vérifie que le ui_table avec filtrage sur colonnes spécifiques génère les bons attributs"""
        template = """
            {% load elixir_toolkit_tags %}
            {% ui_table css_classes="is-striped" filterable=True filter_columns="0,2" %}
                <thead>
                    <tr><th>Nom</th><th>Statut</th><th>Email</th></tr>
                </thead>
                <tbody>
                    <tr><td>Test</td><td>OK</td><td>test@example.com</td></tr>
                </tbody>
            {% end_ui_table %}
        """
        rendered = self.render_template(template)
        
        # Vérifie la présence des attributs de filtrage avec colonnes
        self.assertIn('data-filterable="true"', rendered)
        self.assertIn('data-filter-columns="0,2"', rendered)

    def test_ui_table_filterable_with_target(self):
        """Vérifie que le ui_table avec filtrage et cible spécifique génère les bons attributs"""
        template = """
            {% load elixir_toolkit_tags %}
            {% ui_table css_classes="is-striped" filterable=True filter_target="#search-input" %}
                <thead>
                    <tr><th>Nom</th><th>Statut</th></tr>
                </thead>
                <tbody>
                    <tr><td>Test</td><td>OK</td></tr>
                </tbody>
            {% end_ui_table %}
        """
        rendered = self.render_template(template)
        
        # Vérifie la présence des attributs de filtrage avec cible
        self.assertIn('data-filterable="true"', rendered)
        self.assertIn('data-filter-target="#search-input"', rendered)

    def test_ui_table_filterable_with_id(self):
        """Vérifie que le ui_table avec filtrage et identifiant personnalisé génère les bons attributs"""
        template = """
            {% load elixir_toolkit_tags %}
            {% ui_table css_classes="is-striped" filterable=True filter_id="my-custom-table" filter_columns="1" %}
                <thead>
                    <tr><th>Nom</th><th>Statut</th></tr>
                </thead>
                <tbody>
                    <tr><td>Test</td><td>OK</td></tr>
                </tbody>
            {% end_ui_table %}
        """
        rendered = self.render_template(template)
        
        # Vérifie la présence des attributs de filtrage avec identifiant
        self.assertIn('data-filterable="true"', rendered)
        self.assertIn('data-filter-id="my-custom-table"', rendered)
        self.assertIn('data-filter-columns="1"', rendered)


class ToolkitStepperTest(ToolkitBaseTest):
    STEPS = ["Identification", "Question secrète", "Nouveau mot de passe"]

    def render_stepper(self, arguments="", **context):
        template = "{% load elixir_toolkit_tags %}{% ui_stepper steps " + arguments + " %}"
        return self.render_template(template, {"steps": self.STEPS, **context})

    def test_stepper_basic_render(self):
        """Vérifie la liste ordonnée, les numéros et les libellés"""
        rendered = self.render_stepper()

        self.assertIn('<ol class="ui-stepper " aria-label="Progression">', rendered)
        self.assertEqual(rendered.count('class="ui-stepper-step"'), 3)
        for label in self.STEPS:
            self.assertIn(f'<span class="ui-stepper-label">{label}</span>', rendered)
        self.assertNotIn('aria-current', rendered)
        self.assertNotIn('fa-check', rendered)

    def test_stepper_current_marks_previous_steps_done(self):
        """Par défaut, les étapes avant l'étape active sont complétées"""
        rendered = self.render_stepper("current=3")

        self.assertEqual(rendered.count('class="ui-stepper-step is-done"'), 2)
        self.assertIn('class="ui-stepper-step is-current" aria-current="step"', rendered)
        self.assertEqual(rendered.count('fa-check'), 2)
        self.assertIn('Étape 2 terminée', rendered)

    def test_stepper_explicit_completed(self):
        """Les étapes complétées peuvent être passées explicitement"""
        rendered = self.render_stepper('current=1 completed="2,3"')

        self.assertIn('class="ui-stepper-step is-current"', rendered)
        self.assertEqual(rendered.count('class="ui-stepper-step is-done"'), 2)

        rendered = self.render_stepper("current=2 completed=done", done=[])
        self.assertNotIn('is-done', rendered)

    def test_stepper_dict_steps(self):
        """Les étapes acceptent une description et une icône"""
        steps = [
            {"label": "Salarié", "description": "Identité", "icon": "fas fa-user"},
            {"label": "Observations"},
        ]
        rendered = self.render_stepper("current=2 css_classes='mb-0'", steps=steps)

        self.assertIn('<ol class="ui-stepper mb-0"', rendered)
        self.assertIn('<span class="ui-stepper-description">Identité</span>', rendered)
        # Étape complétée : la coche remplace l'icône
        self.assertNotIn('fas fa-user', rendered)

        rendered = self.render_stepper("current=1", steps=steps)
        self.assertIn('<i class="fas fa-user" aria-hidden="true"></i>', rendered)


class ToolkitDateInputTest(ToolkitBaseTest):
    """`ElixirToolkitConfig.ready()` patche `forms.DateInput` au démarrage : le
    `DateField` standard de Django suffit, sans widget spécifique à retenir.
    """

    def _form(self, data=None, initial=None):
        class DateForm(forms.Form):
            date_effet = forms.DateField(label="Date d'effet", required=False)

        return DateForm(data=data, initial=initial)

    def test_plain_date_field_renders_native_input(self):
        rendered = str(self._form()["date_effet"])

        self.assertIn('type="date"', rendered)
        self.assertIn('name="date_effet"', rendered)

    def test_plain_date_field_uses_iso_format(self):
        rendered = str(self._form(initial={"date_effet": date(2024, 2, 1)})["date_effet"])

        self.assertIn('value="2024-02-01"', rendered)

    def test_explicit_date_input_widget_is_native_too(self):
        class DateForm(forms.Form):
            date_effet = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))

        rendered = str(DateForm(initial={"date_effet": date(2024, 2, 1)})["date_effet"])

        self.assertIn('type="date"', rendered)
        self.assertIn('value="2024-02-01"', rendered)

    def test_explicit_format_stays_prioritary(self):
        rendered = forms.DateInput(format="%d/%m/%Y").render("date_fin", date(2024, 2, 1))

        self.assertIn('value="01/02/2024"', rendered)

    def test_date_field_cleans_iso_value(self):
        form = self._form(data={"date_effet": "2024-02-01"})

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["date_effet"], date(2024, 2, 1))

    def test_datetime_and_time_inputs_are_untouched(self):
        self.assertNotIn('type="date"', forms.DateTimeInput().render("d", None))
        self.assertNotIn('type="date"', forms.TimeInput().render("t", None))

    def test_explicit_widget_override_still_wins(self):
        class DateForm(forms.Form):
            date_effet = forms.DateField(widget=forms.TextInput)

        self.assertIn('type="text"', str(DateForm()["date_effet"]))

    def test_toolkit_assets_loads_date_input_css_and_js(self):
        rendered = self.render_template("{% load elixir_toolkit_tags %}{% toolkit_assets %}")

        self.assertIn('elixir_toolkit/css/date-input.css', rendered)
        self.assertIn('elixir_toolkit/js/date-input.js', rendered)


class ToolkitMaxLengthTest(ToolkitBaseTest):
    """`limit_length` / `FormMaxLengthFieldMixin` : blocage navigateur via
    `data-max-length` (max-length.js) et validation serveur équivalente.
    """

    def _form(self, data=None, widget=None):
        class MessageForm(forms.Form):
            message = forms.CharField(required=False, widget=widget or forms.Textarea)

        form = MessageForm(data=data)
        limit_length(form.fields["message"], 10)
        return form

    def _rich_widget(self):
        # Classe posée par django_ckeditor_5.widgets.CKEditor5Widget
        return forms.Textarea(attrs={"class": "django_ckeditor_5"})

    def test_text_field_gets_native_maxlength_and_data_attribute(self):
        rendered = str(self._form()["message"])

        self.assertIn('maxlength="10"', rendered)
        self.assertIn('data-max-length="10"', rendered)

    def test_text_field_rejects_too_long_value(self):
        form = self._form(data={"message": "x" * 11})

        self.assertFalse(form.is_valid())
        self.assertIn("message", form.errors)

    def test_text_field_counts_crlf_as_one_char(self):
        form = self._form(data={"message": "12345\r\n789"})

        self.assertTrue(form.is_valid())

    def test_rich_text_field_has_no_native_maxlength(self):
        rendered = str(self._form(widget=self._rich_widget())["message"])

        self.assertNotIn('maxlength=', rendered)
        self.assertIn('data-max-length="10"', rendered)

    def test_rich_text_field_counts_visible_text_only(self):
        form = self._form(data={"message": "<p><strong>" + "&amp;" * 10 + "</strong></p>"}, widget=self._rich_widget())

        self.assertTrue(form.is_valid())

    def test_rich_text_field_rejects_too_long_visible_text(self):
        form = self._form(data={"message": "<p>" + "x" * 11 + "</p>"}, widget=self._rich_widget())

        self.assertFalse(form.is_valid())
        self.assertIn("message", form.errors)

    def test_mixin_reads_limits_from_form_meta(self):
        class MessageForm(forms.Form):
            message = forms.CharField(required=False)
            other = forms.CharField(required=False)

            class Meta:
                fields_max_length = {"message": 5, "unknown": 5}

        class BaseView:
            def get_form(self, form_class=None):
                return MessageForm(data={"message": "x" * 6, "other": "x" * 6})

        class View(FormMaxLengthFieldMixin, BaseView):
            pass

        form = View().get_form()

        self.assertFalse(form.is_valid())
        self.assertIn("message", form.errors)
        self.assertNotIn("other", form.errors)

    def test_mixin_view_limits_take_precedence(self):
        class MessageForm(forms.Form):
            message = forms.CharField(required=False)

            class Meta:
                fields_max_length = {"message": 5}

        class BaseView:
            def get_form(self, form_class=None):
                return MessageForm(data={"message": "x" * 6})

        class View(FormMaxLengthFieldMixin, BaseView):
            fields_max_length = {"message": 6}

        self.assertTrue(View().get_form().is_valid())

    def test_toolkit_assets_loads_max_length_js_after_ckeditor_loader(self):
        rendered = self.render_template("{% load elixir_toolkit_tags %}{% toolkit_assets %}")

        self.assertIn('elixir_toolkit/js/max-length.js', rendered)
        self.assertLess(
            rendered.index('elixir_toolkit/js/ckeditor-load-external-plugins.js'),
            rendered.index('elixir_toolkit/js/max-length.js'),
        )
