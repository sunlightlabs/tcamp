from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic.base import TemplateView

from reg.views import *
from reg.badges import *

urlpatterns = patterns('',
    url(r'^$', register),
    url(r'^override/$', register_override),
    url(r'^price/$', price_check),
    url(r'^save/$', save),
    url(r'^thanks/$', TemplateView.as_view(template_name="reg/thanks.html")),
    url(r'^whos-going/$', whos_going),

    url(r'^reports/overview/$', stats),
    url(r'^reports/volunteers.csv$', volunteer_export),
    url(r'^reports/attendees.csv$', attendee_export),

    url(r'^badges\.(?P<format>json|csv|zip)$', attendees),
    url(r'^badges/(?P<barcode>[A-Za-z0-9]{22})\.json$', attendee),
    url(r'^badges/qrcode/(?P<barcode>[A-Za-z0-9]+)\.(?P<format>svg|png)$', qrcode_image),
    url(r'^badges/types.json', ticket_types),
    url(r'^badges/new$', new_sale),
    url(r'^badges/cf_config.json', cardflight_config),
)

admin.autodiscover()