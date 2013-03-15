from django.forms.util import ErrorList
from django.utils.safestring import mark_safe


class BootstrapErrorList(ErrorList):
    def __unicode__(self):
        return self.as_alerts()

    def as_alerts(self):
        if not self:
            return u''
        return mark_safe(u'<div class="alert alert-error">%s</div>' % ''.join(
            [u'<p class="error">%s</p>' % e for e in self]
        ))
