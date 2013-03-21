import datetime

from dateutil.parser import parse as dateparse
from django.core.management.base import BaseCommand, make_option
from django.utils import timezone

from sked.models import Session, Event
from twit.models import SessionBlockTweet


class Command(BaseCommand):
    help = '''Generates Session tweets for a given timeslot.'''

    option_list = BaseCommand.option_list + (
        make_option('--event-id',
                    action='store',
                    dest='event_id',
                    default=Event.objects.current().id,
                    help='''The ID of the event to tweet sessions for
                            '''),
        make_option('--timeslot',
                    action='store',
                    dest='timeslot',
                    default='next',
                    help='''The ISO datetime that the events being tweeted
                            should start at'''),
        make_option('--skip-if-delta',
                    action='store',
                    dest='skipdelta',
                    default='600',
                    help='''A timedelta in seconds that the timeslot should fall
                            within in order to trigger tweet generation'''),
    )

    def handle(self, *args, **options):
        event = Event.objects.get(pk=int(options.get('event_id')))
        timeslot = options.get('timeslot')
        skipdelta = options.get('skipdelta')

        if skipdelta:
            skipdelta = datetime.timedelta(seconds=int(options.get('skipdelta')))
        else:
            skipdelta = None

        if timeslot == 'next':
            sessions = Session.objects.next().filter(event=event)
            timeslot = sessions[0].start_time
        else:
            timeslot = dateparse(timeslot).replace(tzinfo=timezone.get_current_timezone())

        if skipdelta is not None and timezone.now() + skipdelta < timeslot:
            print 'Sessions are too far in the future, aborting.'
            return

        try:
            tweet = SessionBlockTweet.objects.get(event=event, timeslot=timeslot,
                                                  previous=None, sent_at=None)
        except SessionBlockTweet.DoesNotExist:
            print 'No tweets have been generated for this timeslot, or tweets have been sent already. Run ./manage.py generatetweets --event-id=%s --timeslot=%s and try again' % (event.id, timeslot.isoformat())
            return

        tweet.send()
        print 'Sent %d tweets for block %s.' % (tweet.total, timeslot.isoformat())
