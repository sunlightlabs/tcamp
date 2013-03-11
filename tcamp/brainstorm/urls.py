from django.conf.urls.defaults import *
from brainstorm.views import IdeaList, IdeaDetail, CreateIdea
from brainstorm.feeds import SubsiteFeed

# feeds live at rss/latest/site-name/
urlpatterns = patterns('',
    url(r'^rss/latest/$', SubsiteFeed()),
)

urlpatterns += patterns('brainstorm.views',
    url(r'^(?P<slug>[\w-]+)/$', IdeaList.as_view(ordering='most_popular'), name='ideas_popular'),
    url(r'^(?P<slug>[\w-]+)/latest/$', IdeaList.as_view(ordering='latest'), name='ideas_latest'),
    url(r'^(?P<slug>[\w-]+)/(?P<id>\d+)/$', IdeaDetail.as_view(), name='idea_detail'),
    url(r'^(?P<slug>[\w-]+)/new_idea/$', CreateIdea.as_view(), name='new_idea'),
    url(r'^(?P<slug>[\w-]+)/(?P<id>\d+)/votes(?P<format>(\.json))?/?$',
        'vote', name='idea_vote'),
)
