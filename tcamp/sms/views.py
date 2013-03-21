from django_twilio.views import sms
from django_twilio.decorators import twilio_view
from django.utils import timezone
from dateutil.parser import parse as dateparse

from sked.models import Event, Session


@twilio_view
def coming_up(request, message=None, to=None, sender=None, action=None, method=None,
              status_callback=None):
    sessions = Session.objects.filter(event=Event.objects.current(), is_public=True)
    inmsg = request.REQUEST.get('Body').strip() or 'next'
    if inmsg.lower() == 'next':
        message = _as_sms(Session.objects.next())
    if inmsg.lower() == 'now':
        message = _as_sms(Session.objects.current())
    else:
        try:
            ts = dateparse('%s').replace(tzinfo=timezone.get_current_timezone())
            message = _as_sms(sessions.filter(start_time=ts))
        except:
            message = 'Unable to parse that time. Try something like "4:30", or "next"'

    return sms(request, message, to, sender, action, method, status_callback)


def _as_sms(qset):
    msg = 'No events.'
    if not qset.count():
        return msg

    tm = qset[0].start_time.astimezone(timezone.get_current_timezone())
    msg = u'At %s:\n' % tm.strftime('%-I:%M')
    msg += u'\n\n'.join(['%s (%s)' % (s.title, s.location.name) for s in qset])

    return msg
