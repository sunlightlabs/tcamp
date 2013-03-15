import re

from django.conf import settings
from django.core.cache import cache
from django.db import models
from django.template import TemplateSyntaxError
from django.template.loader import get_template, get_template_from_string
from django.db.models.signals import post_save

from markupfield.fields import MarkupField
from taggit.managers import TaggableManager
from pages import validators


DEFAULT_BASE_TEMPLATE = u'''
{{%% extends "{template}" %%}}
{{%% block title %%}}{title} - {{{{ block.super }}}}{{%% endblock %%}}
{blocks}
{{%% block content %%}}{content}{{%% endblock %%}}
'''


class Template(models.Model):
    name = models.CharField(max_length=255, validators=[validators.validate_template_path], unique=True, db_index=True)
    content = models.TextField()
    is_path = models.BooleanField()

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        if self.is_path:
            return u"%s (%s)" % (self.name, self.content)
        return self.name

    @property
    def path(self):
        return self.content if self.is_path else ''

    @property
    def loadable_name(self):
        return "pages:%s" % self.name

    @property
    def template(self):
        return get_template(self.loadable_name)

    @property
    def blocks(self):
        return [b for b in self.template.nodelist.flatten() if b.__class__.__name__ == 'BlockNode']

    @property
    def block_names(self):
        [b.name for b in self.blocks]


class Page(models.Model):

    path = models.CharField(max_length=255)
    template = models.ForeignKey(Template, related_name='pages')
    is_published = models.BooleanField(default=False)

    title = models.CharField(max_length=255)
    content = MarkupField()

    tags = TaggableManager(blank=True)

    class Meta:
        ordering = ('path',)

    def __unicode__(self):
        return self.path

    def get_absolute_url(self):
        return self.path

    @property
    def cache_key(self):
        return 'pages.page.%s' % self.path

    def blocks_as_template_string(self):
        return "\n".join([block.as_template_string() for block in self.blocks.all()])

    def as_template_string(self):
        base_template = getattr(settings, 'PAGES_BASE_TEMPLATE', DEFAULT_BASE_TEMPLATE)
        ctx = {
            "template": self.template.loadable_name,
            "title": self.title,
            "blocks": self.blocks_as_template_string(),
            "content": self.content.rendered,
        }
        return base_template.lstrip("\r\n\t").format(**ctx).replace("%%", '%')

    def as_renderable(self):
        cached = cache.get(self.cache_key)
        if cached:
            return cached
        renderable = None
        tries = 0
        template_string = self.as_template_string()
        while renderable is None and tries < 100:
            try:
                renderable = get_template_from_string(template_string)
            except TemplateSyntaxError, e:
                tries += 1
                # This overrides blocks defined in the render template with
                # block objects, if there are multiples
                # FIXME: Find a better way to do this than catching the block name from exception messages
                match_obj = re.match(r"'block' tag with name '(.+)' appears more than once", e.message)
                if match_obj:
                    dupe_block = match_obj.groups()[0]
                    template_string = re.sub(r'{%% block %s %%}.+{%% endblock( %s)? %%}' % (dupe_block, dupe_block), '',
                                             template_string, count=1, flags=re.MULTILINE)
                else:
                    raise
        if renderable is None:
            raise TemplateSyntaxError('''The Pages app tried and failed to
                remove duplicate blocks from your template. Take a look
                at settings.PAGES_BASE_TEMPLATE''')
        cache.set(self.cache_key, renderable)
        return renderable

    def save(self, **kwargs):
        self.path = "/%s/" % self.path.strip("/")
        super(Page, self).save(**kwargs)


class Block(models.Model):

    name = models.SlugField(max_length=255)
    page = models.ForeignKey(Page, related_name="blocks")
    content = MarkupField()

    def __unicode__(self):
        return u"'%s' on %s" % (self.name, self.page)

    @property
    def cache_key(self):
        return 'pages.block.%s.%s' % (self.page, self.name)

    def as_template_string(self):
        cached = cache.get(self.cache_key)
        if cached:
            return cached
        template_string = '{%% block %s %%}%s{%% endblock %%}' % (self.name, self.content.rendered)
        cache.set(self.cache_key, template_string)
        return template_string


class Chunk(models.Model):

    slug = models.SlugField()
    content = MarkupField()

    class Meta:
        ordering = ('slug',)

    def __unicode__(self):
        return self.slug

    @property
    def cache_key(self):
        return 'pages.chunk.%s' % self.slug


def clear_cache(sender, instance, **kwargs):
    from django.core.cache import cache
    try:
        key = instance.cache_key
    except:
        return
    cache.delete(key)

post_save.connect(clear_cache, sender=Chunk)
post_save.connect(clear_cache, sender=Block)
post_save.connect(clear_cache, sender=Page)
