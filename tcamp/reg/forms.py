from django import forms
from localflavor.us.us_states import STATE_CHOICES
from bootstrap_toolkit.widgets import BootstrapTextInput
import datetime

from reg.models import Sale, Ticket, AMBASSADOR_PROGRAM_CHOICES

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale

class TicketForm(forms.ModelForm):
    #ambassador_program = forms.ChoiceField(initial="no", widget=forms.RadioSelect, choices=AMBASSADOR_PROGRAM_CHOICES, label="Would you like to be part of the TCamp Ambassador Program?")
    class Meta:
        model = Ticket
        exclude = ['event', 'sale', 'success', 'checked_in', 'lobby_day', 'ambassador_program']
        widgets = {
            'twitter': BootstrapTextInput(attrs={'placeholder': "e.g., \"tcampdc\""}),
        }

_current_year = datetime.datetime.now().year
class PaymentForm(forms.Form):
    first_name = forms.CharField(max_length=255)
    last_name = forms.CharField(max_length=255)
    email = forms.EmailField()
    address1 = forms.CharField(max_length=1024, label="Address Line 1")
    address2 = forms.CharField(max_length=1024, label="Address Line 2", required=False)
    city = forms.CharField(max_length=255)
    state = forms.CharField(max_length=255, widget=forms.Select(choices=STATE_CHOICES + (('non-us', 'Outside the USA'),)))
    zip = forms.CharField(max_length=255, label="Zip/Postal Code")

    exp_month = forms.ChoiceField(initial="01", label="Expiration", choices=(("01","01"),("02","02"),("03","03"),("04","04"),("05","05"),("06","06"),("07","07"),("08","08"),("09","09"),("10","10"),("11","11"),("12","12")))
    exp_year = forms.ChoiceField(initial="2014", label="Year", choices=tuple([2*(str(_current_year + i),) for i in xrange(11)]))

    # will be encrypted
    number = forms.CharField(max_length=4096)
    cvv = forms.CharField(max_length=4096)