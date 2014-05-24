from twilio.twiml import Response
from django_twilio.decorators import twilio_view
from django.template.defaultfilters import striptags
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache
from django.utils import timezone
from dateutil.parser import parse as dateparse

from sked.models import Event, Session
import base62


@never_cache
@twilio_view
@require_http_methods(['POST', ])
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
        # First try to base62 decode the message
        try:
            session = _get_session_from_base62(inmsg)
            messages = _as_sms(session)
        except Session.DoesNotExist:
            messages = ["Couldn't find that session.\n\nText 'next' to get the upcoming block of sessions."]
        except ValueError:
            # Not b62-encoded, check to see if it's a time.
            try:
                ts = dateparse(inmsg)
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


def _get_session_from_base62(id):
    session_id = base62.decode(id)
    session = Session.objects.published().filter(pk=session_id)
    return session


def _as_sms(qset):
    msgs = ['No events.\n']
    now = timezone.now()
    if qset.count() > 1:
        return _format_multiple(qset)
    elif qset.count() is 1:
        return _format_single(qset)

    return msgs


def _format_multiple(qset):
    tm = _convert_time(qset[0].start_time)
    if tm.date() == now.date():
        msgs[0] = u'At %s\n' % tm.strftime('%-I:%M')
    else:
        msgs[0] = u'%s at %s\n' % (tm.strftime('%A'), tm.strftime('%-I:%M'))
    msgs[0] += u' (text shortcode for more info):'

    for s in qset:
        line = u'\n%s: \n%s (%s)\n' % (base62.encode(s.id), s.title, s.location.name)
        if len(msgs[-1] + line) <= 150:
            msgs[-1] += line
        else:
            msgs.append(line)

    return msgs


def _format_single(qset):
    sess = qset[0]
    tm = _convert_time(qset[0].start_time)
    msgs = []
    detail = u'''{title}
{time}, in {room}
{speaker_names}

{description}
'''.format(title=sess.title,
           time=u'%s at %s' % (tm.strftime('%A'), tm.strftime('%-I:%M')),
           room=sess.location.name,
           description=striptags(sess.description).replace('&amp;', '&'),
           speaker_names=sess.speaker_names,
           )
    if sess.tags.count():
        detail += u"\n\nTagged: %s" % sess.tag_string

    lines = detail.split('\n')
    msgs.append(lines[0])

    def build_line(tokens, **kwargs):
        maxlen = kwargs.get('maxlen', 146)
        i = kwargs.get('offset', 0)
        curline = []

        while len(u' '.join(curline) + u' %s' % tokens[i]) <= maxlen:
            curline.append(tokens[i])
            i += 1
            if i >= len(tokens):
                break

        return (u' '.join(curline), i)

    for line in lines[1:]:
        if len(msgs[-1] + line) <= 146:
            msgs[-1] += "\n%s" % line
        else:
            if len(line) > 146:
                tokens = line.split()
                offset = 0
                while offset < len(tokens):
                    newline, offset = build_line(tokens, offset=offset)
                    msgs.append(newline)
            else:
                msgs.append(line)

    return msgs


def _convert_time(tm):
    return tm.astimezone(timezone.get_current_timezone())
