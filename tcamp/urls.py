from django.conf.urls import patterns, include, url
from django.views.generic.base import RedirectView
from django.contrib import admin
from sked.views import RedirectFromPk
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^logistics/$', RedirectView.as_view(url="/about/logistics/")),
    url(r'^sessions/$', RedirectView.as_view(url="/schedule/")),
    url(r'^sessions/(?P<pk>[\d]+)/$', RedirectFromPk.as_view()),

    # FIXME: These will need to be updated next year.
    url(r'^submit/$', RedirectView.as_view(url='/schedule/2014/new/')),
    url(r'^fridaywall/$', RedirectView.as_view(url='/schedule/2014/wall/?timeslots=11:30am,12:30pm,1:40pm,2:40pm,3:40pm,4:40pm&refresh=300000')),
    url(r'^saturdaywall/$', RedirectView.as_view(url='/schedule/2014/wall/?timeslots=11:00am,12:00pm,1:10pm,2:10pm,3:10pm,4:10pm&refresh=300000')),
    url(r'^tv/$', RedirectView.as_view(url='/schedule/2014/tv/?refresh=60000')),
    url(r'^wallfail/$', RedirectView.as_view(url='/schedule/2014/wallfail/')),

    url(r'^treenav/', include('treenav.urls')),
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin/varnish/', include('varnishapp.urls')),
    url(r'^staff/$', RedirectView.as_view(url="/staff/login")),
    url(r'^staff/', include('googleauth.urls')),
    url(r'^schedule/', include('sked.urls', namespace='sked')),
    url(r'^sms/', include('sms.urls', namespace='sms')),
    url(r'^camp/', include('camp.urls', namespace='camp')),
    url(r'^api/', include('api.urls')),
    url(r'^login/$', 'camp.views.login', name='login'),
    url(r'^logged-in/$', 'camp.views.logged_in', name='logged_in'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/', 'redirect_field_name': 'next'}, name='logout'),
    url(r'^sponsor-contact/$', 'camp.views.sponsor_contact', name='sponsor_contact'),
    url(r'^register/', include('reg.urls', namespace='reg')),
    url(r'^registration/', include('reg.report_urls', namespace='reg_reports')),
    url(r'^', include('sfapp.urls')),
    url(r'^', include('social.apps.django_app.urls', namespace='social')),
    url(r'^', include('brainstorm.urls', namespace='brainstorm')),
)
