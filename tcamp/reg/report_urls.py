from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic.base import TemplateView

from reg.views import *

urlpatterns = patterns('',
    url(r'^reports/overview/$', stats),
    url(r'^reports/volunteers.csv$', volunteer_export),
    url(r'^reports/attendees.csv$', attendee_export),
)

admin.autodiscover()