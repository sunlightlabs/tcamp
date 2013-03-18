import threading

from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.conf import settings


class SessionConfirmationEmailThread(threading.Thread):
    def __init__(self, session, **kwargs):
        self.session = session
        self.recipient = session.speakers[0]['email']
        super(SessionConfirmationEmailThread, self).__init__(**kwargs)

    def run(self):
        if settings.DEBUG is True:
            return
        send_mail('[TCamp] Session confirmation & edit link',
                  '''Thanks for submitting a session at TCamp! We'll \
                     be reviewing all of the proposals, and you'll get \
                     another email with the pertinent details if your \
                     session is chosen. In the meantime, if you need to \
                     edit anything, visit this URL:

                     {site}{path}?{key}
                     '''.format(site=Site.objects.get_current().domain,
                                path=self.session.get_edit_url(),
                                key=self.session.edit_key),
                  settings.POSTMARK_SENDER,
                  [self.recipient])


class SessionApprovedEmailThread(threading.Thread):
    def __init__(self, session, **kwargs):
        self.session = session
        self.recipient = session.speakers[0]['email']
        super(SessionApprovedEmailThread, self).__init__(**kwargs)

    def run(self):
        if settings.DEBUG is True:
            return
        send_mail('[TCamp] Your Session is on the wall!',
                  '''Your session has been approved and scheduled for:

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
                                location=self.session.location),
                  settings.POSTMARK_SENDER,
                  [self.recipient])
