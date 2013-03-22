from twilio.twiml import Response
from django_twilio.decorators import twilio_view
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from dateutil.parser import parse as dateparse

from sked.models import Event, Session


@twilio_view
@require_http_methods(['POST', ])
def coming_up(request):
    sessions = Session.objects.filter(event=Event.objects.current(), is_public=True)
    r = Response()
    inmsg = request.POST.get('Body').strip() or 'next'
    print inmsg
    if inmsg.lower() == 'next':
        message = _as_sms(Session.objects.next())
    elif inmsg.lower() == 'now':
        message = _as_sms(Session.objects.current())
    else:
        try:
            ts = dateparse('%s').replace(tzinfo=timezone.get_current_timezone())
            message = _as_sms(sessions.filter(start_time__lte=ts, end_time__gte=ts))
        except:
            message = 'Unable to parse that time. Try something like "4:30", or "next"'

    r.sms(message)
    return r


def _as_sms(qset):
    msg = 'No events.'
    now = timezone.now()
    if not qset.count():
        return msg

    tm = qset[0].start_time.astimezone(timezone.get_current_timezone())
    if tm.date() == now.date():
        msg = u'At %s:\n' % tm.strftime('%-I:%M')
    else:
        msg = u'%s at %s:\n' % (tm.strftime('%A'), tm.strftime('%-I:%M'))
    msg += u'\n\n'.join(['%s (%s)' % (s.title, s.location.name) for s in qset])

    return msg
