import threading

from collections import Counter

from django.contrib.sites.models import Site
from django.core.mail import EmailMessage
from django.conf import settings
from django.utils import timezone


class BasePostmarkSessionEmailThread(threading.Thread):
    def __init__(self, session, **kwargs):
        super(BasePostmarkSessionEmailThread, self).__init__(**kwargs)
        self.session = session
        self.sender = settings.POSTMARK_SENDER
        self.recipients = [session.speakers[0]['email']]

    @property
    def should_send(self):
        # feel free to spam admins whenever, but nobody else.
        admins = Counter(dict(settings.ADMINS).values())
        recipients = Counter(self.recipients)
        return not (settings.DEBUG is True and len(list(recipients - admins)) is not 0)

    def run(self):
        headers = {}
        try:
            headers = self.headers
        except AttributeError:
            pass
        if self.should_send:
            EmailMessage(self.subject, self.body, self.sender, self.recipients, headers=headers).send()


class SessionConversionEmailThread(BasePostmarkSessionEmailThread):
    def __init__(self, session, **kwargs):
        super(SessionConversionEmailThread, self).__init__(session, **kwargs)
        self.headers = {'Reply-To': 'wall@transparencycamp.org', }
        self.subject = '[TCamp] Your Idea was Selected!'
        self.body = ("Congratulations! We'd like to include your session "
                     "proposal as part of TransparencyCamp. "
                     "If for any reason you can't "
                     "be in attendence to give your talk, please let us know by emailing "
                     "wall@transparencycamp.org (or replying to this email)."
                     "\n\n"
                     "You'll receive another email once your time slot and room have been "
                     "assigned."
                     "\n\n"
                     "In the meantime, if you need to edit your proposal at all, "
                     "you can use this link: "
                     "http://{site}{path}?{key}"
                     "\n\n"
                     "Looking forward to seeing you at TCamp!"
                     "\n\n"
                     "Sincerely,\n"
                     "The Transparencycamp Team"
                     "").format(site=Site.objects.get_current().domain,
                                path=self.session.get_edit_url(),
                                key=self.session.edit_key)


class SessionConfirmationEmailThread(BasePostmarkSessionEmailThread):
    def __init__(self, session, **kwargs):
        super(SessionConfirmationEmailThread, self).__init__(session, **kwargs)
        self.subject = '[TCamp] Submit confirmation & edit link'
        self.body = ("Thanks for submitting a session at TCamp! We'll "
                     "be reviewing all of the proposals as they come in, "
                     "and you'll get "
                     "another email with the pertinent details if your "
                     "session is chosen. In the meantime, if you need to "
                     "edit anything, visit this URL: "
                     "\n\n"
                     "http://{site}{path}?{key}"
                     "").format(site=Site.objects.get_current().domain,
                                path=self.session.get_edit_url(),
                                key=self.session.edit_key)


class SessionApprovedEmailThread(BasePostmarkSessionEmailThread):
    def __init__(self, session, **kwargs):
        super(SessionApprovedEmailThread, self).__init__(session, **kwargs)
        details = dict(start_time=self.session.start_time.astimezone(
                            timezone.get_current_timezone()
                            ).strftime('%I:%M %p'),
                       location=self.session.location.name,
                       site=Site.objects.get_current().domain,
                       schedule_url=self.session.get_absolute_url())
        self.subject = '[TCamp] {start_time} @ {location} -- Your Session is scheduled!'.format(**details)
        self.body = ("Your session has been approved and scheduled for:"
                     "\n\n"
                     "{start_time} in {location}."
                     "\n\n"
                     "Please see the registration desk 10 minutes before "
                     "your scheduled time slot if you need an "
                     "adapter to connect your laptop to a VGA projector, "
                     "or ask the wall crew if you have logistical or timing "
                     "questions."
                     "\n\n"
                     "Your session's permalink page (http://{site}{schedule_url}) has an "
                     "etherpad on it for collaborative notetaking. To help keep "
                     "a good record of the discussion that goes on during your talk, "
                     "you may want to mention to the group that it's available."
                     "\n\n"
                     "Also, note that since it's published, your proposal can no longer be "
                     "edited. Please see the wall crew with logistical or timing "
                     "questions. ").format(**details)
