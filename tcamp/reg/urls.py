from django.conf.urls import patterns, include, url
from django.contrib import admin

from reg.views import *

urlpatterns = patterns('',
    url(r'^$', register),
)

admin.autodiscover()