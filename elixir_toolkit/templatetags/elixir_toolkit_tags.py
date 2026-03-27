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
    is_multi = False

    if filters and len(filters) > 0:
        first = filters[0]

        # Si déjà liste de listes
        if isinstance(first, (list, tuple)) and len(first) > 0 and isinstance(first[0], (list, tuple)):
            is_multi = True
        else:
            # 🔥 NORMALISATION : transformer en liste de listes
            filters = [filters]
            is_multi = True

    return {
        'filters': filters,
        'identifier': identifier,
        'is_multi': is_multi
    }
    

@register.inclusion_tag('elixir_toolkit/components/list.html')
def ui_list(items, title_field="title", desc_field="description", extra_field=None, 
            icon_field=None, tag_label_field=None, tag_icon_field=None, 
            link_url_name=None, **kwargs):
    """
    Composant de liste générique avec support de badge/tag.
    """
    processed_items = []
    for item in items:
        # Helper pour récupérer une valeur d'un dict ou d'un objet
        get_val = lambda field: getattr(item, field, item.get(field)) if isinstance(item, dict) else getattr(item, field, None)
        
        processed_items.append({
            'title': get_val(title_field) or "",
            'description': get_val(desc_field) or "",
            'extra': get_val(extra_field),
            'icon': get_val(icon_field) or "receipt",
            # Données du Tag (badge)
            'tag_label': get_val(tag_label_field) if tag_label_field else None,
            'tag_icon': get_val(tag_icon_field) if tag_icon_field else "user",
            'obj': item 
        })

    return {
        'items': processed_items,
        'link_url_name': link_url_name,
        'css_classes': kwargs.get('css_classes', '')
    }