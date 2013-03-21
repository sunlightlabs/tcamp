import datetime
import hashlib

from django.conf import settings
from django.core.urlresolvers import reverse, Resolver404
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from jsonfield import JSONField
from timedelta.fields import TimedeltaField
from taggit.managers import TaggableManager

from sked.email import SessionConfirmationEmailThread


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
    session_length = TimedeltaField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, related_name='sked_events')

    objects = EventManager()

    class Meta:
        ordering = ('-start_date', )

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        try:
            return reverse('sked:session_list', kwargs={
                'event_slug': self.slug,
            })
        except Resolver404:
            return reverse('sked:session_list')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:50].rstrip('-')
        super(Event, self).save(*args, **kwargs)

    @property
    def url(self):
        return self.get_absolute_url()


def get_current_event():
    return Event.objects.current()


class Location(models.Model):
    name = models.CharField(max_length=255)
    event = models.ForeignKey(Event, related_name='locations', default=get_current_event)
    is_official = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-event__start_date', 'name')

    def __unicode__(self):
        return self.name

    def related_label(self):
        return "{0} at {1} ({2})".format(self.name, self.event.name,
                                         'official' if self.is_official else 'unofficial')

    @staticmethod
    def autocomplete_search_fields():
        return ("id__iexact", "name__icontains",)


class SessionManager(models.Manager):
    def today(qset):
        today = datetime.date.today()
        return qset.filter(start_time__year=today.year,
                           start_time__month=today.month,
                           start_time__day=today.day,
                           is_public=True)

    def published(qset):
        return qset.filter(is_public=True)

    def current(qset):
        now = datetime.datetime.now()
        current_time_slot = qset.filter(start_time__lte=now).aggregate(
            timeslot=models.Max('start_time')).get('timeslot')
        return qset.filter(start_time=current_time_slot,
                           is_public=True)

    def next(qset):
        now = datetime.datetime.now()
        next_time_slot = qset.filter(start_time__gt=now).aggregate(
            timeslot=models.Min('start_time')).get('timeslot')
        return qset.filter(start_time=next_time_slot,
                           is_public=True)


class Session(models.Model):
    title = models.CharField(max_length=128)
    slug = models.SlugField()
    description = models.TextField(blank=True, help_text="Markdown is supported.")
    speakers = JSONField(help_text='An array of objects. Each must contain a "name" attribute', default='[]')
    extra_data = JSONField(blank=True, default='{}')
    tags = TaggableManager(blank=True)
    is_public = models.BooleanField(default=False)

    event = models.ForeignKey(Event, related_name='sessions')
    location = models.ForeignKey(Location, blank=True, null=True)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_by = models.ForeignKey(User, blank=True, null=True, related_name="approved_sked_sessions")

    objects = SessionManager()

    class Meta:
        unique_together = (('event', 'slug'), )
        ordering = ('-event__start_date', 'start_time', )

    def __unicode__(self):
        return "%s at %s" % (self.title, self.event)

    def get_absolute_url(self):
        url = reverse('sked:session_detail', kwargs={
            'event_slug': self.event.slug,
            'slug': self.slug,
        })

        return url

    def get_edit_url(self):
        url = reverse('sked:edit_session', kwargs={
            'event_slug': self.event.slug,
            'slug': self.slug,
        })

        return url

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:50].rstrip('-')
        if not self.end_time and self.start_time:
            self.end_time = self.start_time + self.event.session_length
        return super(Session, self).save(*args, **kwargs)

    @property
    def speaker_names(self):
        try:
            names = [spkr['name'] for spkr in self.speakers]
            return ', '.join(names)
        except:
            return ''

    @property
    def contact_email(self):
        try:
            return self.speakers[0]['email']
        except:
            return None

    @property
    def url(self):
        return self.get_absolute_url()

    @property
    def edit_key(self):
        return hashlib.sha1(u'%s:%s' % (settings.SECRET_KEY, self.created_at)).hexdigest()


@receiver(post_save, sender=Session)
def send_confirmation_email(sender, **kwargs):
    instance = kwargs['instance']
    created = kwargs['created']
    if (not created or
            not (len(instance.speakers) and instance.speakers[0].get('email')) or
            instance.is_public):
        return
    SessionConfirmationEmailThread(instance).run()
