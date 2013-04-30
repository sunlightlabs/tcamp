from django.db import models
from django.template.defaultfilters import truncatechars
from django.utils import timezone
from sked.models import Event, Session
from twit.threads import SendTweetThread


class TweetTooLongError(Exception):
    def __init__(self, msg=None):
        self.msg = msg
        if not self.msg:
            self.msg = 'Adding this session would result in a tweet longer than 140 characters.'


class AlreadyAssignedError(Exception):
    def __init__(self, msg=None):
        self.msg = msg
        if not self.msg:
            self.msg = 'This session already belongs to a tweet in this sequence.'


class Tweet(models.Model):
    sent_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True

    def send(self):
        # ''' This is weird. It can only be called from the first tweet in
        #     a series, raising NotImplementedError if called on a non-initial tweet.
        #     It spins off a thread to make the actual api calls, which
        #     manages state within the series.
        #     '''
        if self.previous:
            raise NotImplementedError('Serial tweets can only be sent from the beginning.')
        SendTweetThread(self).start()

    @property
    def is_sent(self):
        return self.sent_at is not None


class SessionBlockTweetManager(models.Manager):
    def unsent(qs):
        return qs.filter(sent_at=None, previous=None)


class SessionBlockTweet(Tweet):
    timeslot = models.DateTimeField()
    event = models.ForeignKey(Event, related_name="session_tweets")
    session_ids = models.CommaSeparatedIntegerField(max_length=128,
                                                    blank=True, default="")
    previous = models.OneToOneField('SessionBlockTweet', blank=True,
                                    null=True, unique=True, related_name="next")

    objects = SessionBlockTweetManager()

    class Meta:
        ordering = ('-timeslot', 'id')

    def __unicode__(self):
        try:
            return 'Tweet %s of %s for %s at %s' % (
                self.index + 1, self.total, self.timeslot, self.event)
        except:
            return 'Tweet for %s at %s' % (self.timeslot, self.event)

    def touch(self):
        self._seq = None
        self._sessions = None

    def get_sequence(self):
        try:
            if self._seq is not None:
                return self._seq
        except AttributeError:
            pass
        seq = []
        cursor = self
        while cursor.previous:
            cursor = cursor.previous
        seq.append(cursor)
        while True:
            try:
                cursor = cursor.next
                seq.append(cursor)
            except SessionBlockTweet.DoesNotExist:
                break

        self._seq = seq
        return self.get_sequence()

    def first_in_sequence(self):
        seq = self.get_sequence()
        return seq[0]

    def get_session_ids(self):
        try:
            return [int(id) for id in self.session_ids.split(',')]
        except:
            return []

    def add_session(self, session):
        if self.length < 140:
            assigned = [id for tweet in self.get_sequence() for id in tweet.get_session_ids()]
            if session.id in assigned:
                raise AlreadyAssignedError()
            locally_assigned = self.get_session_ids()
            locally_assigned.append(session.id)
            self.session_ids = ','.join([str(id) for id in locally_assigned])
            self.touch()
            if self.length > 140:
                if self.sessions.count() > 1:
                    self.remove_session(session)
                    raise TweetTooLongError()
        else:
            raise TweetTooLongError()

    def remove_session(self, session):
        self.session_ids = ','.join([str(id) for
                                     id in self.get_session_ids() if
                                     id != session.id])
        self.touch()

    @property
    def sessions(self):
        try:
            if self._sessions is not None:
                return self._sessions
        except AttributeError:
            pass
        try:
            self._sessions = Session.objects.filter(id__in=self.get_session_ids())
        except ValueError:
            self._sessions = Session.objects.none()
        return self.sessions

    @property
    def index(self):
        seq = self.get_sequence()
        return seq.index(self)

    @property
    def is_first(self):
        return self.previous is None

    @property
    def is_last(self):
        try:
            return self.next is None
        except SessionBlockTweet.DoesNotExist:
            return True

    @property
    def total(self):
        seq = self.get_sequence()
        return len(seq)

    @property
    def text(self):
        txt = u''
        if self.is_first:
            txt += u'Coming up at %s: ' % (self.timeslot
                                           .astimezone(timezone.get_current_timezone())
                                           .strftime('%-I:%M'))

        txt += u', '.join(['%s (%s)' % (truncatechars(s.title, 120) if
                                        self.sessions.count() is 1 else
                                        s.title, s.location.name) for
                          s in self.sessions])

        return txt

    @property
    def length(self):
        return len(self.text)
