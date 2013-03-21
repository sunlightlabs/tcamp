from django.conf.urls import patterns, include, url
from django.views.generic.base import RedirectView
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^treenav/', include('treenav.urls')),
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^staff/$', RedirectView.as_view(url="/staff/login")),
    url(r'^staff/', include('googleauth.urls')),
    url(r'^schedule/', include('sked.urls', namespace='sked')),
    url(r'^sms/', include('sms.urls', namespace='sms')),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/', 'redirect_field_name': 'next'}, name='logout'),
    url(r'^', include('social.apps.django_app.urls', namespace='social')),
    url(r'^', include('camp.urls')),
    url(r'^', include('brainstorm.urls', namespace='brainstorm')),
)
