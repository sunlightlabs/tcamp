from django.conf.urls.defaults import *
from django.views.decorators.cache import never_cache
from honeypot.decorators import check_honeypot

from brainstorm.views import IdeaList, IdeaDetail, CreateIdea
from brainstorm.feeds import SubsiteFeed

# feeds live at rss/latest/site-name/
urlpatterns = patterns(
    '',
    url(r'^rss/latest/$', SubsiteFeed()),
)

urlpatterns += patterns(
    'brainstorm.views',
    url(r'^(?P<slug>[\w-]+)/$', never_cache(IdeaList.as_view(ordering='most_popular')), name='ideas_popular'),
    url(r'^(?P<slug>[\w-]+)/latest/$', never_cache(IdeaList.as_view(ordering='latest')), name='ideas_latest'),
    url(r'^(?P<slug>[\w-]+)/(?P<id>\d+)/$', never_cache(IdeaDetail.as_view()), name='idea_detail'),
    url(r'^(?P<slug>[\w-]+)/new_idea/$', never_cache(check_honeypot(CreateIdea.as_view())), name='new_idea'),
    url(r'^(?P<slug>[\w-]+)/(?P<id>\d+)/votes(?P<format>(\.json))?/?$',
        'vote', name='idea_vote'),
)
