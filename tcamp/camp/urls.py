from django.conf.urls import patterns, include, url


urlpatterns = patterns(
    'camp.views',
    url(r'^subscribe/$', 'email_subscribe', name="create_email_subscriber"),
)
