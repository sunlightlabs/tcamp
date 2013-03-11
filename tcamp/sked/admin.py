from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from taggit.models import Tag, TaggedItem
from sked.models import Event, Session


class SessionTagsListFilter(admin.SimpleListFilter):
    title = _('tag')

    parameter_name = 'tag'

    def lookups(self, request, model_admin):
        items = TaggedItem.objects.filter(content_type__name='session', content_type__app_label='sked')
        tags = Tag.objects.filter(taggit_taggeditem_items__in=items).distinct().order_by('name')
        return tuple([(t.name, t.name) for t in tags])

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        return queryset.filter(tags__name__in=[self.value()])


class SessionInline(admin.StackedInline):
    model = Session


class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'start_date',
                    'end_date', 'is_public', )
    list_filter = ('is_public', )
    date_hierarchy = 'start_date'
    prepopulated_fields = {'slug': ('name', )}
    search_fields = ('name', )
    inlines = (SessionInline, )


class SessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'speaker_names', 'start_time', 'is_public',
                    'published_by', )
    list_filter = (SessionTagsListFilter, 'published_by', )
    prepopulated_fields = {'slug': ('title', )}
    search_fields = ('title', 'description', 'speaker_names')
    date_hierarchy = 'start_time'

admin.site.register(Event, EventAdmin)
admin.site.register(Session, SessionAdmin)
