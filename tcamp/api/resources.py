from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.constants import ALL, ALL_WITH_RELATIONS

from sked.models import Event, Session, Location


class EventResource(ModelResource):
    url = fields.CharField(attribute='url')
    sessions = fields.ToManyField('api.resources.SessionResource', 'sessions', blank=True)

    class Meta:
        queryset = Event.objects.select_related().filter(is_public=True)
        filtering = {
            'name': ALL,
            'slug': ALL,
            'start_date': ALL,
            'end_date': ALL,
        }


class SessionResource(ModelResource):
    event = fields.ToOneField(EventResource, 'event', null=True)
    location = fields.ToOneField('api.resources.LocationResource', 'location', null=True, full=True)
    speaker_names = fields.CharField(attribute='speaker_names')
    url = fields.CharField(attribute='url')

    class Meta:
        queryset = Session.objects.published().select_related().prefetch_related('location')
        filtering = {
            'title': ALL,
            'slug': ALL,
            'speakers': ALL,
            'extra_data': ALL,
            'event': ALL_WITH_RELATIONS,
            'location': ALL_WITH_RELATIONS,
            'start_time': ALL,
            'end_time': ALL,
        }


class LocationResource(ModelResource):
    event = fields.ToOneField(EventResource, 'event', null=True)
    sessions = fields.ToManyField(SessionResource, 'sessions', null=True)

    class Meta:
        queryset = Location.objects.prefetch_related('event', 'sessions')
        filtering = {
            'name': ALL,
            'is_official': ALL,
            'event': ALL_WITH_RELATIONS,
            'sessions': ALL_WITH_RELATIONS,
        }
