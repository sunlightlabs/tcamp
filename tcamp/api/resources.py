from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.constants import ALL, ALL_WITH_RELATIONS

from sked.models import Event, Session, Location


class EventResource(ModelResource):
    class Meta:
        queryset = Event.objects.select_related().filter(is_public=True)
        filtering = {
            'name': ALL,
            'slug': ALL,
            'start_date': ALL,
            'end_date': ALL,
        }


class SessionResource(ModelResource):
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
    class Meta:
        queryset = Location.objects.prefetch_related('events', 'sessions')
        filtering = {
            'name': ALL,
            'is_official': ALL,
            'event': ALL_WITH_RELATIONS,
            'sessions': ALL_WITH_RELATIONS,
        }
