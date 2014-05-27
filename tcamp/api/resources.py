from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.authentication import BasicAuthentication

from taggit.models import Tag
from sked.models import Event, Session, Location
from brainstorm.models import Subsite, Idea
from camp.models import SponsorshipLevel, Sponsor, EmailSubscriber


class TagResource(ModelResource):
    class Meta:
        queryset = Tag.objects.all()


class EventResource(ModelResource):
    url = fields.CharField(attribute='url')
    sessions = fields.ToManyField('api.resources.SessionResource', 'sessions', blank=True)

    class Meta:
        queryset = Event.objects.select_related().filter(is_public=True)
        excludes = ['is_public', 'label', 'session_label', 'created_at',
                    'updated_at', 'created_by']
        filtering = {
            'name': ALL,
            'slug': ALL,
            'start_date': ALL,
            'end_date': ALL,
        }


class SessionResource(ModelResource):
    event = fields.ToOneField(EventResource, 'event', null=True)
    location = fields.ToOneField('api.resources.LocationResource', 'location', null=True, full=True)
    tags = fields.ToManyField(TagResource, 'tags', null=True, full=True)
    speaker_names = fields.CharField(attribute='speaker_names')
    url = fields.CharField(attribute='url')

    class Meta:
        queryset = Session.objects.published().select_related().prefetch_related('location')
        excludes = ['speakers', 'extra_data', 'is_public', 'created_at',
                    'updated_at', 'published_by']
        filtering = {
            'title': ALL,
            'slug': ALL,
            'speakers': ALL,
            'extra_data': ALL,
            'event': ALL_WITH_RELATIONS,
            'location': ALL_WITH_RELATIONS,
            'start_time': ALL,
            'end_time': ALL,
        }


class LocationResource(ModelResource):
    event = fields.ToOneField(EventResource, 'event', null=True)
    sessions = fields.ToManyField(SessionResource, 'sessions', null=True)

    class Meta:
        queryset = Location.objects.prefetch_related('event', 'sessions')
        excludes = ['created_at', 'updated_at']
        filtering = {
            'name': ALL,
            'is_official': ALL,
            'event': ALL_WITH_RELATIONS,
            'sessions': ALL_WITH_RELATIONS,
        }


class SubsiteResource(ModelResource):
    url = fields.CharField(attribute='get_absolute_url')

    class Meta:
        queryset = Subsite.objects.all().select_related()
        excludes = ['scoring_algorithm', 'theme', 'idea_label',
                    'ideas_per_page', 'upvote_label', 'upvotes_label',
                    'allow_downvote', 'downvote_label', 'downvotes_label',
                    'voted_label']
        filtering = {
            'name': ALL,
            'slug': ALL,
            'post_status': ALL,
        }


class IdeaResource(ModelResource):
    class Meta:
        queryset = Idea.objects.public().select_related()
        excludes = ['email', 'is_public', 'user', '']
        filtering = {
            'title': ALL,
            'name': ALL,
            'score': ALL,
        }


class SponsorshipLevelResource(ModelResource):
    event = fields.ToOneField(EventResource, 'event', null=True, full=True)

    class Meta:
        queryset = SponsorshipLevel.objects.all().select_related()
        excludes = ['created_at', 'updated_at']
        filtering = {
            'name': ALL,
            'slug': ALL,
            'price': ALL,
            'event': ALL_WITH_RELATIONS,
        }


class SponsorResource(ModelResource):
    sponsorship = fields.ToOneField(SponsorshipLevelResource, 'sponsorship', null=True, full=True)

    class Meta:
        queryset = Sponsor.objects.all().select_related()
        excludes = ['created_at', 'updated_at', 'order']
        filtering = {
            'name': ALL,
            'sponsorship': ALL_WITH_RELATIONS,
        }


class EmailSubscriberResource(ModelResource):
    event = fields.ToOneField(EventResource, 'event', null=True, full=False)

    class Meta:
        queryset = EmailSubscriber.objects.all()
        filtering = {
            'email': ALL,
            'event': ALL_WITH_RELATIONS,
        }
        authentication = BasicAuthentication()
