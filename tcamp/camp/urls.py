from django.conf.urls import patterns, include, url

urlpatterns = patterns('camp.views',
    # url(r'^$', 'tcamp.views.home', name='home'),
    url(r'login/$', 'login', name='login'),
    url(r'^logged-in/$', 'logged_in', name='logged_in'),
)

# urlpatterns += patterns('',
#     url(r'^$', 'pages.views.page', {'path': ''}, name="home"),
# )
