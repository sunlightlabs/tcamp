import reversion

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from taggit.models import Tag, TaggedItem
from pages.models import Page, Template, Chunk, Block


class PostTagsListFilter(admin.SimpleListFilter):
    title = _('tag')

    parameter_name = 'tag'

    def lookups(self, request, model_admin):
        items = TaggedItem.objects.filter(content_type__name='page', content_type__app_label='pages')
        tags = Tag.objects.filter(taggit_taggeditem_items__in=items).distinct().order_by('name')
        return tuple([(t.name, t.name) for t in tags])

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        return queryset.filter(tags__name__in=[self.value()])


class BlockInline(admin.StackedInline):
    model = Block


class BlockAdmin(reversion.VersionAdmin):
    list_display = ('__unicode__', )
    list_filter = ('page', )


class PageAdmin(reversion.VersionAdmin):
    list_display = ('title', 'path', 'template', 'is_published')
    list_filter = (PostTagsListFilter, )
    inlines = [BlockInline]


class TemplateAdmin(reversion.VersionAdmin):
    list_display = ('name', 'path', 'is_path')


class ChunkAdmin(reversion.VersionAdmin):
    list_display = ('slug',)


admin.site.register(Block, BlockAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(Template, TemplateAdmin)
admin.site.register(Chunk, ChunkAdmin)
