from dateutil.parser import parse as dateparse
from django.core.management.base import BaseCommand, make_option
from django.utils import timezone

from sked.models import Event
from twit.models import SessionBlockTweet


class Command(BaseCommand):
    help = '''Deletes Session tweets for a given timeslot.'''

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
                    default=None,
                    help='''The ISO datetime that the events being tweeted
                            should start at'''),
    )

    def handle(self, *args, **options):
        event = Event.objects.get(pk=int(options.get('event_id')))
        timeslot = dateparse(options.get('timeslot')).replace(tzinfo=timezone.get_current_timezone())

        tweets = SessionBlockTweet.objects.filter(event=event, timeslot=timeslot)
        if tweets.count():
            confirm = raw_input('Are you SURE you want to destroy tweets for timeslot %s? [yN]:' % tweets[0].timeslot.isoformat())
        if confirm == 'y':
            tweets.delete()
