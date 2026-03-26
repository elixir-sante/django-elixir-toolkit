# elixir_toolkit/templatetags/elixir_toolkit_tags.py
from django import template
from django.utils.safestring import mark_safe
from django.templatetags.static import static
from django.forms.utils import flatatt
import ast

register = template.Library()

@register.inclusion_tag('elixir_toolkit/components/toolkit_css.html')
def toolkit_css(version="1.0.0"):
    return {
        "bulma_version": version
    }
@register.inclusion_tag('elixir_toolkit/components/button.html')
def ui_button(text, css_classes="", icon=None, icon_right=False, href=None, **kwargs):
    # Nettoyage des clés (data_id -> data-id)
    html_attrs = {k.replace('_', '-'): v for k, v in kwargs.items()}
    
    return {
        'text': text,
        'css_classes': css_classes,
        'icon': icon,
        'icon_right': icon_right,
        'href': href,
        'attrs': flatatt(html_attrs),
    }

@register.inclusion_tag('elixir_toolkit/components/button.html')
def ui_button_primary(text, css_classes="", **kwargs):
    new_classes = f"is-primary {css_classes}".strip()
    return ui_button(text, css_classes=new_classes, **kwargs)


@register.inclusion_tag('elixir_toolkit/components/button.html')
def ui_button_secondary(text, css_classes="", **kwargs):
    """Bouton secondaire - Couleur 'Link' (Bleu) en dur"""
    new_classes = f"is-link {css_classes}".strip()
    return ui_button(text, css_classes=new_classes, **kwargs)


@register.inclusion_tag('elixir_toolkit/components/select.html')
def ui_select(name, options, element_id=None, selected=None, placeholder="Choisissez...", icon=None, css_classes=""):
    if isinstance(options, str):
        try:
            options = ast.literal_eval(options)
        except (ValueError, SyntaxError):
            options = []

    if isinstance(options, dict):
        options = options.items()

    return {
        'name': name,
        'element_id': element_id or f"id_{name}",
        'options': options,
        'selected': str(selected) if selected else None,
        'placeholder': placeholder,
        'icon': icon,
        'css_classes': css_classes,
    }
    
@register.inclusion_tag('elixir_toolkit/components/filter_bar.html')
def ui_filter_bar(filters, identifier="default"):
    """
    filters: la liste envoyée par la vue
    identifier: pour différencier si tu as plusieurs barres sur la même page
    """
    return {
        'filters': filters,
        'identifier': identifier,
    }