import threading

from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.conf import settings


class BasePostmarkSessionEmailThread(threading.Thread):
    def __init__(self, session, **kwargs):
        self.session = session
        self.sender = settings.POSTMARK_SENDER
        self.recipients = [session.speakers[0]['email']]
        return super(BasePostmarkSessionEmailThread, self).__init__(self, **kwargs)

    @property
    def should_send(self):
        # feel free to spam admins whenever, but nobody else.
        return not (settings.DEBUG is True and self.recipient not in dict(settings.ADMINS).values())

    def run(self):
        if self.should_send:
            send_mail(self.subject, self.body, self.sender, self.recipients)


class SessionConfirmationEmailThread(BasePostmarkSessionEmailThread):
    def __init__(self, session, **kwargs):
        self = super(SessionConfirmationEmailThread, self).__init__(self, session, **kwargs)
        self.subject = '[TCamp] Session confirmation & edit link'
        self.body = '''Thanks for submitting a session at TCamp! We'll \
                     be reviewing all of the proposals, and you'll get \
                     another email with the pertinent details if your \
                     session is chosen. In the meantime, if you need to \
                     edit anything, visit this URL:

                     {site}{path}?{key}
                     '''.format(site=Site.objects.get_current().domain,
                                path=self.session.get_edit_url(),
                                key=self.session.edit_key)
        return self


class SessionApprovedEmailThread(BasePostmarkSessionEmailThread):
    def __init__(self, session, **kwargs):
        self = super(SessionConfirmationEmailThread, self).__init__(self, session, **kwargs)
        self.subject = '[TCamp] Your Session is on the wall!'
        self.body = '''Your session has been approved and scheduled for:

                     {start_time} in {location}.

                     Please see the registration desk 10 minutes before \
                     your scheduled time slot if you need an \
                     adapter to connect your laptop to a VGA projector, \
                     or ask the wall crew if you have logistical or timing \
                     questions.

                     Now that it's published, your proposal can no longer be \
                     edited. Please see the wall crew with logistical or timing \
                     questions.
                     '''.format(start_time=self.session.strftime('%h:%m'),
                                location=self.session.location)
        return self
