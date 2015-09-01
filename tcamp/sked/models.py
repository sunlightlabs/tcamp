import hashlib
import re
import datetime

from django.conf import settings
from django.core.urlresolvers import reverse, Resolver404
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.utils import timezone
from dateutil.parser import parse as dateparse
from jsonfield import JSONField
from markupfield.fields import MarkupField
from timedelta.fields import TimedeltaField
from taggit.managers import TaggableManager
from taggit.models import TaggedItemBase

from brainstorm.models import Idea
from sked.email import (SessionConfirmationEmailThread,
                        SessionConversionEmailThread)
# from reg.models import Ticket
from tagger import extract_tags as tgr

import base62


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
    start_date = models.DateField(db_index=True)
    end_date = models.DateField(blank=True, null=True, db_index=True)
    is_public = models.BooleanField(default=False, db_index=True)
    is_over = models.BooleanField(default=False, db_index=True)
    registration_is_open = models.BooleanField(default=False)
    registration_url = models.URLField(blank=True, default='')
    session_submission_is_open = models.BooleanField(default=False)

    label = models.CharField(max_length=64, default='event')
    session_label = models.CharField(max_length=64, default='session')
    session_length = TimedeltaField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, related_name='sked_events', blank=True, null=True)

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
        return (self.pk == Event.objects.current().pk and not self.is_over)

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
    is_official = models.BooleanField(default=False, db_index=True)
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
        return u"{0} at {1} ({2})".format(self.name, self.event.name,
                                          'official' if self.is_official else 'unofficial')

    @property
    def etherpad_host(self):
        if self.event.created_at.year >= 2015:
            return "https://tcamp.etherpad.mozilla.org"
        else:
            return "http://pad.transparencycamp.org"

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

    def current(qset, time="now"):
        try:
            now = dateparse(time)
        except (ValueError, AttributeError):
            now = timezone.now()
        current_time_slot = qset.filter(start_time__lte=now, end_time__gt=now, is_public=True).aggregate(
            timeslot=models.Max('start_time')).get('timeslot')
        return qset.select_related().filter(start_time=current_time_slot,
                                            is_public=True).prefetch_related('location')

    def next(qset, time="now"):
        try:
            now = dateparse(time)
        except (ValueError, AttributeError):
            now = timezone.now()
        event = Event.objects.current()
        next_time_slot = qset.filter(start_time__gt=now, event=event, is_public=True).aggregate(
            timeslot=models.Min('start_time')).get('timeslot')
        return qset.select_related().filter(start_time=next_time_slot,
                                            is_public=True).prefetch_related('location')


class AutoTags(TaggedItemBase):
    content_object = models.ForeignKey('Session')


class Session(models.Model):
    title = models.CharField(max_length=102)
    slug = models.SlugField(db_index=True)
    description = MarkupField(blank=True, markup_type='markdown', help_text="Markdown is supported.")
    speakers = JSONField(help_text='An array of objects. Each must contain a "name" attribute', blank=True, default='[]', db_index=True)
    extra_data = JSONField(blank=True, default='{}')
    tags = TaggableManager(blank=True, help_text="Help us schedule your session so that it doesn't conflict with other sessions around the same topics. Some example tags: Open data, International, Federal, State, Parliamentary Monitoring, Social Media, Design, Lobbying.")
    auto_tags = TaggableManager(blank=True, through=AutoTags)
    auto_tags.rel.related_name = '+'
    user_notes = models.TextField(blank=True, default='', help_text='Note in this space if you need to request a specific timeslot, or make sure you have a projector, etc. We can\'t make guarantees about anything, but we\'ll do our best.')
    hashtag = models.CharField(max_length=140, blank=True, null=True, help_text="Help others find and share info about your session! Include the '#'.")

    is_public = models.BooleanField(default=False, db_index=True)
    has_notes = models.BooleanField(default=True)
    notes_slug = models.SlugField(blank=True, help_text="Set this to override the default slug (i.e., If you want more than one session to have the same pad.")

    event = models.ForeignKey(Event, related_name='sessions')
    location = models.ForeignKey(Location, blank=True, null=True, related_name='sessions')
    start_time = models.DateTimeField(blank=True, null=True, db_index=True)
    end_time = models.DateTimeField(blank=True, null=True, db_index=True)

    admin_notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_by = models.ForeignKey(User, blank=True, null=True, related_name="approved_sked_sessions")

    objects = SessionManager()

    class Meta:
        unique_together = (('event', 'slug'), )
        ordering = ('-event__start_date', 'start_time', )

    def __unicode__(self):
        return u"%s at %s" % (self.title, self.event)

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
        # get the old instance for dirty tracking
        try:
            old = Session.objects.get(pk=self.id)
        except Session.DoesNotExist, AttributeError:
            old = None

        # create a slug if doesn't exist
        if not self.slug:
            self.slug = slugify(self.title)[:50].rstrip('-')
            normalized_slug = re.sub(r'[\d]+$', '', self.slug)
            count = 0
            while Session.objects.filter(slug=self.slug,
                                         event=self.event).count():
                count += 1
                self.slug = '%s%s' % (normalized_slug, count)

        # set the right end time if it should be set
        if self.start_time and (not self.end_time or
                                (old.start_time != self.start_time and
                                 old.end_time == self.end_time)):
            self.end_time = self.start_time + self.event.session_length

        super(Session, self).save(*args, **kwargs)

    @property
    def speaker_names(self):
        try:
            names = [spkr['name'] for spkr in self.speakers]
            return u', '.join(names)
        except:
            return u''

    @property
    def contact_email(self):
        try:
            return self.speakers[0]['email']
        except:
            return None

    @property
    def attending_day1(self):
        ticket = self._get_current_ticket()
        if ticket is None:
            return False
        return ticket.attend_day1

    @property
    def attending_day2(self):
        ticket = self._get_current_ticket()
        if ticket is None:
            return False
        return ticket.attend_day2

    @property
    def leader(self):
        try:
            return self.speakers[0]['name']
        except:
            return None

    @property
    def tag_string(self):
        tags = self.tags.all() or self.auto_tags.all()
        return u', '.join(t.name for t in tags)

    @property
    def url(self):
        return self.get_absolute_url()

    @property
    def edit_key(self):
        return hashlib.sha1(u'%s:%s' % (settings.SECRET_KEY, self.created_at)).hexdigest()

    @property
    def needs_projector(self):
        try:
            return self.extra_data['has_slides']
        except:
            return u'Unspecified'

    @property
    def etherpad_url(self):
        if self.event.created_at.year >= 2015:
            pad_subdomain = '/'
        else:
            pad_subdomain = '/p/'

        if self.notes_slug:
            slug = '{}-{}'.format(self.event.slug, self.notes_slug)
        elif self.event.created_at.year >= 2014:
            slug = '{}-{}'.format(self.event.slug, self.slug[0:30])
        else:
            slug = self.slug

        if self.event.created_at.year >= 2015:
            params = '?fullScreen=1&sidebar=0'
        else:
            params = ''

        url = self.location.etherpad_host + pad_subdomain + slug + params
        return url

    @property
    def sms_shortcode(self):
        return base62.encode(self.id)

    def _get_current_ticket(self):
        # Do this here to avoid a circular import of reg/sked models.
        from reg.models import Ticket
        from sked.models import Event
        try:
            return self.ticket
        except AttributeError:
            current_event = Event.objects.current()
            try:
                ticket = Ticket.objects.filter(email__iexact=self.contact_email,
                                               event_id=current_event.id)
            except ValueError:
                return None
            try:
                self.ticket = ticket[0]
                return self.ticket
            except IndexError:
                pass


class SentEmail(models.Model):
    recipients = models.CharField(max_length=255)
    sender = models.EmailField(max_length=127)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    session = models.ForeignKey(Session, blank=True, null=True, on_delete=models.SET_NULL)
    sent_at = models.DateTimeField()

    def __init__(self, *args, **kwargs):
        email = kwargs.get('email_thread')
        try:
            del(kwargs['email_thread'])
        except:
            pass
        super(SentEmail, self).__init__(*args, **kwargs)
        if email:
            self.recipients = ', '.join(email.recipients)
            self.sender = email.sender
            self.subject = email.subject
            self.body = email.body
            self.session = email.session
            self.sent_at = timezone.now()

    def __unicode__(self):
        u"Email to %s for %s sent %s" % (self.recipients, self.session.title, self.sent_at.isoformat())


@receiver(post_save, sender=Session)
def autogenerate_tags(sender, **kwargs):
    instance = kwargs['instance']
    tags = tgr('%s %s' % (instance.title, instance.description.raw))
    instance.auto_tags.set(*[tag.string for tag in tags if len(tag.string) <= 100])


@receiver(post_save, sender=Session)
def send_confirmation_email(sender, **kwargs):
    instance = kwargs['instance']
    created = kwargs['created']
    if (not created or
            not (len(instance.speakers) and instance.speakers[0].get('email')) or
            instance.is_public):
        return
    # if this exists as a brainstorm idea, we want to send a different email
    print (instance.title, instance.description.raw)
    if Idea.objects.filter(title=instance.title,
                           description=instance.description.raw).count() > 0:
        thread = SessionConversionEmailThread(instance)
    else:
        thread = SessionConfirmationEmailThread(instance)
    if thread.should_send:
        print u'%s SHOULD SEND' % thread.__class__.__name__
        SentEmail(email_thread=thread).save()
        thread.start()
