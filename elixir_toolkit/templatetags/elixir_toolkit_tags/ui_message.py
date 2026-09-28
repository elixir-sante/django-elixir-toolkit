from django import template
from django.forms.utils import flatatt
from django.utils.html import escape
from django.utils.safestring import mark_safe

# Import the register from parent module
from . import register


@register.inclusion_tag('elixir_toolkit/components/message.html')
def ui_message_base(content, color="primary", title=None, css_classes="", is_safe=False, **kwargs):
    """
    Composant Message Bulma.
    
    Usage :
        {% ui_message content="Mon message ici" color="primary" %}
        {% ui_message content="Mon message avec titre" title="Titre" color="info" %}
        {% ui_message content="Mon message" color="success" css_classes="mb-4" %}
    
    Paramètres :
        - content (requis) : Contenu HTML du message
        - color (optionnel) : Couleur du message (primary, info, success, warning, danger) - défaut: primary
        - title (optionnel) : Titre du message (sera affiché dans le header)
        - css_classes (optionnel) : Classes CSS supplémentaires
        - is_safe (optionnel) : Si True, le contenu est marqué comme safe (pas d'échappement HTML) - défaut: False
        - **kwargs : Attributs HTML supplémentaires (ex: data-id, id, etc.)
    """
    color_class = f"is-{color}" if color else "is-primary"
    html_attrs = {k.replace('_', '-'): v for k, v in kwargs.items()}

    # Django marque les littéraux passés aux tags de template comme "safe"
    # (mark_safe dans django.template.base.Variable) : un simple
    # {{ content }} dans le template ne les échapperait jamais. On échappe
    # donc inconditionnellement (escape() agit même sur les SafeString),
    # sauf demande explicite is_safe=True.
    if is_safe:
        content = mark_safe(content) if content is not None else ""
    else:
        content = escape(content) if content is not None else ""
    title = escape(title) if title is not None else None

    return {
        'content': content,
        'color_class': color_class,
        'title': title,
        'css_classes': css_classes,
        'attrs': flatatt(html_attrs),
    }


@register.inclusion_tag('elixir_toolkit/components/message.html')
def ui_message(content, title=None, css_classes="", is_safe=False, **kwargs):
    """Message avec couleur primary."""
    return ui_message_base(content, color="primary", title=title, css_classes=css_classes, is_safe=is_safe, **kwargs)


@register.inclusion_tag('elixir_toolkit/components/message.html')
def ui_message_info(content, title=None, css_classes="", is_safe=False, **kwargs):
    """Message avec couleur info (cyan)."""
    return ui_message_base(content, color="info", title=title, css_classes=css_classes, is_safe=is_safe, **kwargs)


@register.inclusion_tag('elixir_toolkit/components/message.html')
def ui_message_success(content, title=None, css_classes="", is_safe=False, **kwargs):
    """Message avec couleur success (vert)."""
    return ui_message_base(content, color="success", title=title, css_classes=css_classes, is_safe=is_safe, **kwargs)


@register.inclusion_tag('elixir_toolkit/components/message.html')
def ui_message_warning(content, title=None, css_classes="", is_safe=False, **kwargs):
    """Message avec couleur warning (jaune)."""
    return ui_message_base(content, color="warning", title=title, css_classes=css_classes, is_safe=is_safe, **kwargs)


@register.inclusion_tag('elixir_toolkit/components/message.html')
def ui_message_danger(content, title=None, css_classes="", is_safe=False, **kwargs):
    """Message avec couleur danger (rouge)."""
    return ui_message_base(content, color="danger", title=title, css_classes=css_classes, is_safe=is_safe, **kwargs)
