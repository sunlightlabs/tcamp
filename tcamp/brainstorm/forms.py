from django.conf import settings
from django.contrib.sites.models import Site
from django.forms import ModelForm, ValidationError
from akismet import Akismet

from brainstorm.models import Idea


class IdeaForm(ModelForm):
    class Meta:
        model = Idea
        fields = ('title', 'name', 'email', 'description',
                  'user', 'subsite')

    def __init__(self, **kwargs):
        try:
            self.request = kwargs['request']
            del kwargs['request']
        except:
            pass
        super(IdeaForm, self).__init__(**kwargs)

    def clean(self):
        request = self.request
        site = Site.objects.get_current().domain
        ak = Akismet(settings.AKISMET_KEY, site)
        ak.verify_key()
        if ak.comment_check(self.cleaned_data.get('description').encode('ascii', 'ignore'), {
                'comment_author': self.cleaned_data.get('name').encode('ascii', 'ignore'),
                'comment_author_email': self.cleaned_data.get('email').encode('ascii', 'ignore'),
                'user_ip': request.META.get('HTTP_X_FOWARDED_FOR', request.META['REMOTE_ADDR']),
                'user_agent': request.META.get('HTTP_USER_AGENT'), }):
            raise ValidationError("Your submission contained known spam.")
        return super(IdeaForm, self).clean()
