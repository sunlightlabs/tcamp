from twilio.twiml import Response
from django_twilio.decorators import twilio_view
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from dateutil.parser import parse as dateparse

from sked.models import Event, Session


@twilio_view
@require_http_methods(['POST', ])
def coming_up(request):
    sessions = Session.objects.filter(is_public=True)
    r = Response()
    inmsg = request.POST.get('Body').strip() or 'next'
    if inmsg.lower() == 'next':
        messages = _as_sms(Session.objects.next())
    elif inmsg.lower() == 'now':
        messages = _as_sms(Session.objects.current())
    else:
        try:
            ts = dateparse(inmsg).replace(tzinfo=timezone.get_current_timezone())
            messages = _as_sms(sessions.filter(start_time__lte=ts, end_time__gte=ts))
        except:
            messages = ['Unable to parse that time. Try something like "4:30", or "next"']

    l = len(messages)
    for i, message in enumerate(messages):
        r.sms(message + '\n\n(%d/%d)' % (i+1, l))
    return r


def _as_sms(qset):
    msgs = ['No events.']
    now = timezone.now()
    if not qset.count():
        return msgs

    tm = qset[0].start_time.astimezone(timezone.get_current_timezone())
    if tm.date() == now.date():
        msgs[0] = u'At %s:\n' % tm.strftime('%-I:%M')
    else:
        msgs[0] = u'%s at %s:\n' % (tm.strftime('%A'), tm.strftime('%-I:%M'))

    for s in qset:
        line = u'\n%s (%s)\n' % (s.title, s.location.name)
        if len(msgs[-1] + line) <= 150:
            msgs[-1] += line
        else:
            msgs.append(line)

    return msgs
