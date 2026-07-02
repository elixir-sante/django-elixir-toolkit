from django import template
from django.conf import settings

register = template.Library()

@register.inclusion_tag('elixir_toolkit/liveidentity_script.html')
def render_captcha_script(form_id):
    return {
        'sp_key': getattr(settings, 'LIVEIDENTITY_SP_KEY', ''),
        'form_id': form_id
    }