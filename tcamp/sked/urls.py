from django.conf.urls import patterns, include, url
from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView
from django.views.decorators.cache import never_cache

from sked.views import (SessionList, SessionDetail, CreateSession,
                        UpdateSession, SingleDayView, CurrentTimeslotView)
from sked.models import Event

CURRENT_EVENT = Event.objects.current()

urlpatterns = patterns(
    'sked.views',
    url(r'^new/$', RedirectView.as_view(url=reverse_lazy('sked:new_session', kwargs={'event_slug': CURRENT_EVENT.slug}))),
    url(r'^$', RedirectView.as_view(url=reverse_lazy('sked:session_list', kwargs={'event_slug': CURRENT_EVENT.slug}))),
    url(r'^(?P<event_slug>[\w-]+)/$', never_cache(SessionList.as_view()), name="session_list"),
    url(r'^(?P<event_slug>[\w-]+)/wall/$', never_cache(SingleDayView.as_view(template_name="sked/wall.html")), name="wall"),
    url(r'^(?P<event_slug>[\w-]+)/wallfail/$', never_cache(SingleDayView.as_view(template_name="sked/analog_wall.html")), name="analog_wall"),
    url(r'^(?P<event_slug>[\w-]+)/tv/$', never_cache(CurrentTimeslotView.as_view(template_name="sked/tv.html")), name="tv"),
    url(r'^(?P<event_slug>[\w-]+)/new/$', never_cache(CreateSession.as_view()), name="new_session"),
    url(r'^(?P<event_slug>[\w-]+)/(?P<slug>[\w-]+)/edit/$', never_cache(UpdateSession.as_view()), name="edit_session"),
    url(r'^(?P<event_slug>[\w-]+)/(?P<slug>[\w-]+)/preview/$', SessionDetail.as_view(preview=True), name="session_preview"),
    url(r'^(?P<event_slug>[\w-]+)/(?P<slug>[\w-]+)/$', SessionDetail.as_view(), name="session_detail"),
)
