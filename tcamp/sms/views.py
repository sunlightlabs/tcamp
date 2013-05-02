from twilio.twiml import Response
from django_twilio.decorators import twilio_view
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache
from django.utils import timezone
from dateutil.parser import parse as dateparse

from sked.models import Event, Session


@twilio_view
@require_http_methods(['POST', ])
@never_cache
def coming_up(request):
    sessions = Session.objects.filter(is_public=True, event=Event.objects.current())
    r = Response()
    inmsg = request.POST.get('Body').strip() or 'next'
    if inmsg.lower() == 'next':
        messages = _as_sms(Session.objects.next())
    elif inmsg.lower() == 'now':
        messages = _as_sms(Session.objects.current())
    elif inmsg.lower() == 'lunch':
        try:
            now = timezone.now()
            messages = _as_sms(Session.objects.filter(start_time__day=now.day,
                                                      start_time__month=now.month,
                                                      start_time__year=now.year,
                                                      title__icontains='lunch')[0])
        except IndexError:
            messages = ["No lunch on the schedule for today, sorry.\n"]
    else:
        try:
            ts = dateparse(inmsg).replace(tzinfo=timezone.get_current_timezone())
            if ts.hour is 0 and ts.minute is 0:
                messages = ["A lot of stuff can happen in a whole day! Try specifying a time.\n"]
            else:
                messages = _as_sms(sessions.filter(start_time__lte=ts, end_time__gte=ts))
        except:
            messages = ["Welcome to TCamp!\n\nOptions:\nnow: Current sessions\nnext: Next timeslot\nlunch: When's lunch?\n<time>, eg. 4:30pm: What's happening at 4:30?\n"]

    l = len(messages)
    for i, message in enumerate(messages):
        r.sms(message + '\n(%d/%d)' % (i+1, l))
    return r


def _as_sms(qset):
    msgs = ['No events.\n']
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
