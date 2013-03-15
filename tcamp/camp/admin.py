from django.contrib import admin
from camp.models import SponsorshipLevel, Sponsor


class SponsorAdmin(admin.ModelAdmin):
    list_display = ('name', 'sponsorship', 'order', )
    list_editable = ('order', )
    list_filter = ('sponsorship', )
    search_fields = ('name', )


class SponsorshipLevelAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'event', 'price',
                    'order', )
    list_editable = ('order', )
    list_filter = ('event__name', )
    prepopulated_fields = {'slug': ('name', )}
    search_fields = ('name', 'event', )


admin.site.register(Sponsor, SponsorAdmin)
admin.site.register(SponsorshipLevel, SponsorshipLevelAdmin)


'''
Monkeypatches for vendored admins
'''

''' Adds an admin action to brainstorm.idea to convert to sked.session '''
from brainstorm.admin import IdeaAdmin
import brainstorm.admin
from sked.models import Event, Session
import json


def convert_to_session(modeladmin, request, queryset):
    event = Event.objects.current()
    for idea in queryset:
        speakers = [{
            'name': idea.name,
            'email': idea.email,
            'display_email': False,
        }]
        defaults = {
            'description': idea.description,
            'speakers': json.dumps(speakers),
        }
        obj, created = Session.objects.get_or_create(
            event=event,
            title=idea.title,
            defaults=defaults
        )
        if not created:
            obj.__dict__.update(**defaults)
            obj.save()
convert_to_session.short_description = 'Convert selected ideas to sessions'
IdeaAdmin.actions = IdeaAdmin.actions + [convert_to_session, ]
