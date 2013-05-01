import requests
import json

from django.contrib import admin
from django.core.cache import cache
from django.conf import settings

from brainstorm.models import Idea
from brainstorm.admin import IdeaAdmin
from sked.models import Event, Session
from sked.admin import SessionAdmin
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


''' Adds is_registered, day_one, and day_two booleans to ideas to
    show whether the submitter has purchased a ticket, and their attendance plans'''


def _get_registration(**kwargs):
    cache_key = 'reg:attendees:json2'
    url = settings.REGISTRATION_API_ENDPOINT
    user = settings.REGISTRATION_API_USER
    pwd = settings.REGISTRATION_API_PASSWORD
    json_data = cache.get(cache_key)
    if not json_data:
        try:
            json_data = requests.get(url, auth=(user, pwd)).content
            cache.set(cache_key, json_data, 86400 * 100)  # hold on for 100 days
        except Exception:
            pass
    if not json_data:
        return None

    email = kwargs.get('email') or ''
    name = kwargs.get('name') or ''
    attendees = json.loads(json_data).get('attendees', [])
    names = ["%s %s" % (x.get('first_name', '').lower(), x.get('last_name', '').lower()) for x in attendees]
    emails = [x.get('email', '').lower() for x in attendees]
    index = None
    try:
        index = emails.index(email.lower())
    except ValueError:
        pass
    if index is None:
        try:
            index = names.index(name.lower())
        except ValueError:
            pass
    if index is None:
        return None
    return attendees[index]


def is_registered(**kwargs):
    return _get_registration(**kwargs) is not None


def day_one(**kwargs):
    reg = _get_registration(**kwargs)
    if reg is None:
        return False
    if reg['which_days'].lower() in ['', 'saturday']:
        return True
    return False


def day_two(**kwargs):
    reg = _get_registration(**kwargs)
    if reg is None:
        return False
    if reg['which_days'].lower() in ['', 'sunday']:
        return True
    return False


def idea_is_registered(instance):
    return is_registered(email=instance.email, name=instance.name)
idea_is_registered.boolean = True
idea_is_registered.short_description = 'Is registered?'
Idea.is_registered = idea_is_registered


def idea_day_one(instance):
    return day_one(email=instance.email, name=instance.name)
idea_day_one.boolean = True
idea_day_one.short_description = 'Attending day 1?'
Idea.day_one = idea_day_one


def idea_day_two(instance):
    return day_two(email=instance.email, name=instance.name)
idea_day_two.boolean = True
idea_day_two.short_description = 'Attending day 2?'
Idea.day_two = idea_day_two

IdeaAdmin.list_display = list(IdeaAdmin.list_display) + ['day_one', 'day_two']


def session_is_registered(instance):
    return is_registered(email=instance.contact_email, name=instance.leader)
session_is_registered.boolean = True
session_is_registered.short_description = 'Is registered?'
Session.is_registered = session_is_registered


def session_day_one(instance):
    return day_one(email=instance.contact_email, name=instance.leader)
session_day_one.boolean = True
session_day_one.short_description = 'Attending day 1?'
Session.day_one = session_day_one


def session_day_two(instance):
    return day_two(email=instance.contact_email, name=instance.leader)
session_day_two.boolean = True
session_day_two.short_description = 'Attending day 2?'
Session.day_two = session_day_two

SessionAdmin.list_display = list(SessionAdmin.list_display) + ['day_one', 'day_two']
