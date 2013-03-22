from tastypie.resources import ModelResource

from sked.models import Event, Session, Location


class EventResource(ModelResource):
    class Meta:
        queryset = Event.objects.select_related().filter(is_public=True)


class SessionResource(ModelResource):
    class Meta:
        queryset = Session.objects.select_related().published().prefetch_related('location')


class LocationResource(ModelResource):
    class Meta:
        queryset = Location.objects.prefetch_related('events').prefetch_related('sessions')
