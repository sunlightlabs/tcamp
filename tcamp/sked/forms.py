from django.forms import ModelForm, ValidationError, widgets
from sked.models import Session


class SessionForm(ModelForm):
    class Meta:
        model = Session
        fields = ('title', 'description', 'tags', 'speakers',
                  'extra_data', 'user_notes', 'event', )
        widgets = {
            'title': widgets.TextInput(attrs={'data-limit': '60'}),
            'description': widgets.Textarea(attrs={'data-limit': '1000', 'resizable': 'false'}),
            'user_notes': widgets.Textarea(attrs={'data-limit': '140', 'rows': '4'}),
        }

    def clean_speakers(self):
        speakers = self.cleaned_data.get('speakers')
        if not len(speakers):
            raise ValidationError('This field cannot be blank.')
        if not speakers[0].get('email') or not speakers[0].get('name'):
            raise ValidationError('The first speaker must have a name and email address.')
        for speaker in speakers:
            if not speaker['name']:
                raise ValidationError('All speaker names must be filled out.')
        return self.cleaned_data.get('speakers')
