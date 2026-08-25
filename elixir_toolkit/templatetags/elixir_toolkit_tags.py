# elixir_toolkit/templatetags/elixir_toolkit_tags.py
from django import template
from django.forms.utils import flatatt
import ast
from django.template.base import Node

register = template.Library()


@register.filter(name='split')
def split(value):
    if value:
        return value.split()
    return None

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
        'type': kwargs.get('type', 'button'),
        'attrs': flatatt(html_attrs),
    }

@register.inclusion_tag('elixir_toolkit/components/button.html')
def ui_button_primary(text, css_classes="", **kwargs):
    new_classes = f"is-primary {css_classes}".strip()
    return ui_button(text, css_classes=new_classes, **kwargs)


@register.inclusion_tag('elixir_toolkit/components/button.html')
def ui_button_secondary(text, css_classes="", **kwargs):
    """Bouton secondaire - Couleur 'Link' (Bleu) en dur"""
    new_classes = f"is-primary is-outlined {css_classes}".strip()
    return ui_button(text, css_classes=new_classes, **kwargs)


@register.inclusion_tag('elixir_toolkit/components/tabs_scroll_hints.html')
def ui_tabs_scroll_hints():
    """Chevrons de défilement pour une barre d'onglets qui déborde.

    Usage :
        <div class="tabs-scroll-wrapper">
            <div class="tabs">...</div>
            {% ui_tabs_scroll_hints %}
        </div>

    Après un swap HTMX, rappeler loadTabsScrollHints() côté JS.
    """
    return {}


@register.inclusion_tag('elixir_toolkit/components/select.html')
def ui_select(name, options, element_id=None, selected=None, multiple=None, placeholder="Choisissez...", icon=None, css_classes=""):
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
        'selected_list': [str(selected)] if selected else [],
        'placeholder': placeholder,
        'icon': icon,
        'css_classes': css_classes,
        'multiple': multiple,
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
    processed_items = []
    for item in items:
        def get_val(field_name):
            if not field_name:
                return None
            if isinstance(item, dict):
                return item.get(field_name)
            return getattr(item, field_name, None)
        
        processed_items.append({
            'title': get_val(title_field) or "",
            'description': get_val(desc_field) or "",
            'extra': get_val(extra_field),
            'icon': get_val(icon_field) or "receipt",
            'tag_label': get_val(tag_label_field),
            'tag_icon': get_val(tag_icon_field) or "user",
            'obj': item 
        })

    return {
        'items': processed_items,
        'link_url_name': link_url_name,
        'css_classes': kwargs.get('css_classes', '')
    }

class TableBlockNode(Node):
    def __init__(self, css_classes, nodelist):
        self.css_classes = css_classes
        self.nodelist = nodelist

    def render(self, context):
        resolved_classes = self.css_classes.resolve(context) if self.css_classes else ""
        table_content = self.nodelist.render(context)

        # context.render_annotated() gère directement le rendu d'un template avec le contexte actuel
        t = template.loader.get_template('elixir_toolkit/components/table.html')

        with context.push({'css_classes': resolved_classes, 'table_content': table_content}):
            return t.render(context)


@register.tag(name="ui_table")
def ui_table(parser, token):
    """
    Usage:
        {% ui_table css_classes="is-striped" %}
            <thead>...</thead>
            <tbody>...</tbody>
        {% endui_table %}
    """
    bits = token.split_contents()[1:]
    css_classes = None
    
    for bit in bits:
        if bit.startswith("css_classes="):
            val = bit.split("=")[1]
            css_classes = parser.compile_filter(val)

    # Tout ce qui se trouve entre {% ui_table %} et {% end_ui_table %}
    nodelist = parser.parse(('end_ui_table',))
    parser.delete_first_token() # Consomme le end_ui_table

    return TableBlockNode(css_classes, nodelist)


@register.inclusion_tag('elixir_toolkit/components/tag.html')
def ui_tag(text, color="primary", dot=True, css_classes=""):
    """
    Composant Tag / Badge générique Bulma.
    Usage:
        {% ui_tag text="Actif" color="success" %}
    """
    color_class = f"is-{color}" if color else ""

    return {
        'text': text,
        'color_class': color_class,
        'dot': dot,
        'css_classes': css_classes,
    }


@register.inclusion_tag('elixir_toolkit/components/chevron.html')
def ui_chevron(direction="down", size="", css_classes=""):
    """
    Composant Chevron / Icône de direction générique Bulma.
    Usage:
        {% ui_chevron direction="right" %}
    """
    # Sécurité pour s'assurer que la direction est valide
    valid_directions = ['down', 'right', 'up', 'left']
    if direction not in valid_directions:
        direction = 'down'

    return {
        'direction': direction,
        'size': size,
        'css_classes': css_classes,
    }