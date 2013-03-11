from django import template

from pages.models import Chunk

register = template.Library()


@register.simple_tag(name='chunk')
def do_chunk(slug):

    try:
        c = Chunk.objects.get(slug=slug)
        return c.content
    except Chunk.DoesNotExist:
        return ''
