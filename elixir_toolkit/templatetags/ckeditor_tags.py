from django import template

register = template.Library()


@register.inclusion_tag('elixir_toolkit/ckeditor/pre.html', takes_context=True)
def ckeditor_pre(context, upload_url=""):
    """A placer avant {{ form.media }}. `upload_url` : endpoint d'upload du projet."""
    return {
        'upload_url': upload_url,
        'csrf_token': context.get('csrf_token', ''),
    }


@register.inclusion_tag('elixir_toolkit/ckeditor/post.html')
def ckeditor_post():
    """A placer après {{ form }}. Compatible htmx."""
    return {}
