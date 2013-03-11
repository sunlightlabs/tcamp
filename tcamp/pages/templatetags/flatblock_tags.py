from django import template

from pages.templatetags.pages_tags import do_chunk

register = template.Library()


@register.simple_tag
def flatblock(*args, **kwargs):
    return do_chunk(*args, **kwargs)
