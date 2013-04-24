import hashlib

from django.conf import settings
from django.core.urlresolvers import reverse, Resolver404
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.utils import timezone
from jsonfield import JSONField
from markupfield.fields import MarkupField
from timedelta.fields import TimedeltaField
from taggit.managers import TaggableManager

from sked.email import SessionConfirmationEmailThread


class EventManager(models.Manager):
    def current(qset, is_public=True):
        cid = getattr(settings, 'CURRENT_EVENT_ID', 0)
        try:
            conf = qset.select_related().prefetch_related('sessions').get(pk=int(cid))
        except Event.DoesNotExist:
            conf = qset.filter()
            if is_public:
                conf = conf.select_related().prefetch_related('sessions').filter(is_public=True)
            return conf[0]
        return conf

    def public_current(qset, request):
        return Event.objects.current(not request.user.is_staff)


class Event(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, db_index=True)
    description = MarkupField(blank=True)
    overview = MarkupField(blank=True)
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

    @property
    def is_current(self):
        now = timezone.now()
        if self.start_date <= now and self.end_date >= now:
            return True
        return False

    @property
    def is_upcoming(self):
        now = timezone.now()
        if self.start_date > now:
            return True
        return False


class LocationManager(models.Manager):
    def official(qset):
        return qset.filter(is_official=True)

    def with_sessions(qset):
        return qset.filter(has_sessions=True)


class Location(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    event = models.ForeignKey(Event, related_name='locations')
    is_official = models.BooleanField(default=False)
    has_sessions = models.BooleanField(default=True, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = LocationManager()

    class Meta:
        ordering = ('-event__start_date', 'name')

    def __unicode__(self):
        return self.related_label()

    def save(self, *args, **kwargs):
        if not self.event:
            self.event = Event.objects.current()
        super(Location, self).save(*args, **kwargs)

    def related_label(self):
        return "{0} at {1} ({2})".format(self.name, self.event.name,
                                         'official' if self.is_official else 'unofficial')

    @staticmethod
    def autocomplete_search_fields():
        return ("id__iexact", "name__icontains",)


class SessionManager(models.Manager):
    def today(qset):
        today = timezone.now().date()
        return qset.select_related().filter(start_time__year=today.year,
                                            start_time__month=today.month,
                                            start_time__day=today.day,
                                            is_public=True).prefetch_related('location')

    def today_or_first_for_event(qset, event):
        qset = Session.objects.today().filter(event=event)
        if qset.count() is 0:
            try:
                date = Session.objects.filter(event=event).dates('start_time', 'day')[0]
            except IndexError:
                return []
            qset = Session.objects.select_related().filter(event=event,
                                                           start_time__year=date.year,
                                                           start_time__month=date.month,
                                                           start_time__day=date.day,
                                                           is_public=True).prefetch_related('location')
        return qset

    def today_or_first(qset):
        event = Event.objects.current()
        return Session.objects.today_or_first_for_event(event)

    def published(qset):
        return qset.select_related().filter(is_public=True).prefetch_related('location')

    def current(qset):
        now = timezone.now()
        current_time_slot = qset.filter(start_time__lte=now, end_time__gt=now).aggregate(
            timeslot=models.Max('start_time')).get('timeslot')
        return qset.select_related().filter(start_time=current_time_slot,
                                            is_public=True).prefetch_related('location')

    def next(qset):
        now = timezone.now()
        event = Event.objects.current()
        next_time_slot = qset.filter(start_time__gt=now, event=event).aggregate(
            timeslot=models.Min('start_time')).get('timeslot')
        return qset.select_related().filter(start_time=next_time_slot,
                                            is_public=True).prefetch_related('location')


class Session(models.Model):
    title = models.CharField(max_length=102)
    slug = models.SlugField(db_index=True)
    description = MarkupField(blank=True, markup_type='markdown', help_text="Markdown is supported.")
    speakers = JSONField(help_text='An array of objects. Each must contain a "name" attribute', blank=True, default='[]', db_index=True)
    extra_data = JSONField(blank=True, default='{}')
    tags = TaggableManager(blank=True)
    is_public = models.BooleanField(default=False)
    has_notes = models.BooleanField(default=True)

    event = models.ForeignKey(Event, related_name='sessions')
    location = models.ForeignKey(Location, blank=True, null=True, related_name='sessions')
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
