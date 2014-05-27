import requests
import json

from django.contrib import admin
from django.core.cache import cache
from django.conf import settings

from brainstorm.models import Idea
from brainstorm.admin import IdeaAdmin
from sked.models import Event, Session
from sked.admin import SessionAdmin
from camp.models import SponsorshipLevel, Sponsor, EmailSubscriber


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

class EmailSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'event')
    list_filter = ('event__name', )
    search_fields = ('email', )

admin.site.register(Sponsor, SponsorAdmin)
admin.site.register(SponsorshipLevel, SponsorshipLevelAdmin)
admin.site.register(EmailSubscriber, EmailSubscriberAdmin)


'''
Monkeypatches for vendored admins
'''


def convert_to_session(modeladmin, request, queryset):
    ''' Adds an admin action to brainstorm.idea to convert to sked.session '''
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


def mark_as_spam(modeladmin, request, queryset):
    ''' Marks a brainstorm item as spam '''
    ak = Akismet(settings.AKISMET_KEY, site)
    ak.verify_key()
    for idea in queryset:
        ak.submit_spam(idea.encode('ascii', 'ignore'), {
            'comment_author': idea.name.encode('ascii', 'ignore'),
            'comment_author_email': idea.email.encode('ascii', 'ignore'),
            # 'user_ip': idea.ip,
            # 'user_agent': idea.useragent,
        })
        idea.is_public = False
        idea.save()

mark_as_spam.short_description = 'Mark selected ideas as spam'
IdeaAdmin.actions = IdeaAdmin.actions + [mark_as_spam, ]


def attending_day1(instance):
    ''' Adds a badge for ideas or sessions to indicate attendance '''
    return instance.attending_day1
attending_day1.boolean = True
attending_day1.short_description = "Day 1"


def attending_day2(instance):
    ''' Adds a badge for ideas or sessions to indicate attendance '''
    return instance.attending_day2
attending_day2.boolean = True
attending_day2.short_description = "Day 2"


IdeaAdmin.list_display = list(IdeaAdmin.list_display) + [attending_day1,
                                                         attending_day2]
SessionAdmin.list_display = list(SessionAdmin.list_display) + [attending_day1,
                                                               attending_day2]
