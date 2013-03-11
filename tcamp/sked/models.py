import datetime

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from jsonfield import JSONField
from taggit.managers import TaggableManager


class EventManager(models.Manager):
    def current(qset, is_public=True):
        cid = getattr(settings, 'CURRENT_EVENT_ID', 0)
        try:
            conf = qset.get(pk=int(cid))
        except Event.DoesNotExist:
            conf = qset.filter()
            if is_public:
                conf = conf.filter(is_public=True)
            return conf[0]
        return conf

    def public_current(qset, request):
        return Event.objects.current(not request.user.is_staff)


class Event(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_public = models.BooleanField(default=False)
    registration_is_open = models.BooleanField(default=False)
    registration_url = models.URLField(blank=True, default='')

    label = models.CharField(max_length=64, default='event')
    session_label = models.CharField(max_length=64, default='session')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, related_name='sked_events')

    objects = EventManager()

    class Meta:
        ordering = ('-start_date', )

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        pass

    @property
    def url(self):
        return self.get_absolute_url()


class SessionManager(models.Manager):
    def today(qset):
        today = datetime.date.today()
        return qset.filter(start_time__year=today.year,
                           start_time__month=today.month,
                           start_time__day=today.day)

    def published(qset):
        return qset.filter(is_public=True)

    def current(qset):
        now = datetime.datetime.now()
        return qset.filter(start_time__lte=now).aggregate(models.Max('start_time'))

    def next(qset):
        now = datetime.datetime.now()
        return qset.filter(start_time__gt=now).aggregate(models.Min('start_time'))


class Session(models.Model):
    title = models.CharField(max_length=128)
    slug = models.SlugField()
    description = models.TextField(blank=True)
    speakers = JSONField(help_text='An array of objects. Each must contain a "name" attribute', default='[]')
    extra_data = JSONField(blank=True, default='{}')
    tags = TaggableManager()
    is_public = models.BooleanField(default=False)

    event = models.ForeignKey(Event, related_name='sessions')
    location = models.CharField(max_length=128, blank=True, null=True)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_by = models.ForeignKey(User, related_name="approved_sked_sessions")

    objects = SessionManager()

    class Meta:
        unique_together = (('event', 'slug'), )
        ordering = ('start_time', )

    def __unicode__(self):
        return "%s at %s" % (self.title, self.event)

    def get_absolute_url(self):
        pass

    @property
    def speaker_names(self):
        try:
            names = [spkr['name'] for spkr in self.speakers]
            return ', '.join(names)
        except:
            return ''

    @property
    def url(self):
        return self.get_absolute_url()
