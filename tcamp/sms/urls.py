from django.conf.urls import patterns, url

urlpatterns = patterns('sms.views',
    # url(r'^$', 'tcamp.views.home', name='home'),
    url(r'^$', 'coming_up'),
)
