from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic.base import TemplateView

from reg.views import *
from reg.badges import qrcode_svg, attendees

urlpatterns = patterns('',
    url(r'^$', register),
    url(r'^price/$', price_check),
    url(r'^save/$', save),
    url(r'^thanks/$', TemplateView.as_view(template_name="reg/thanks.html")),
    url(r'^whos-going/$', whos_going),

    url(r'^reports/overview/$', stats),
    url(r'^reports/volunteers.csv$', volunteer_export),
    url(r'^reports/attendees.csv$', attendee_export),

    url(r'^badges/qrcode/(?P<barcode>[A-Za-z0-9]+)\.(?P<format>svg|png)$', qrcode_svg),
    url(r'^badges/export\.(?P<format>json|csv)$', attendees),
)

admin.autodiscover()