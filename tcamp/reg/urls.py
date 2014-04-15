from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic.base import TemplateView

from reg.views import *

urlpatterns = patterns('',
    url(r'^$', register),
    url(r'^price/$', price_check),
    url(r'^save/$', save),
    url(r'^thanks/$', TemplateView.as_view(template_name="reg/thanks.html")),
    url(r'^whos-going/$', whos_going),

    url(r'^reports/overview/$', stats),
    url(r'^reports/volunteers.csv$', volunteer_export),
)

admin.autodiscover()