from django.conf.urls.defaults import patterns, url, include
from tastypie.api import Api

from api.resources import *

v1 = Api(api_name='1.0')
v1.register(EventResource())
v1.register(SessionResource())
v1.register(LocationResource())
v1.register(SubsiteResource())
v1.register(IdeaResource())
v1.register(SponsorshipLevelResource())
v1.register(SponsorResource())

urlpatterns = patterns('',
    url(r'^', include(v1.urls)),
)
