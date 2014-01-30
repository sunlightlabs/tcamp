from django import forms
from localflavor.us import forms as us_forms

from reg.models import Sale, Ticket, AMBASSADOR_PROGRAM_CHOICES

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale

class TicketForm(forms.ModelForm):
    ambassador_program = forms.ChoiceField(initial="no", widget=forms.RadioSelect, choices=AMBASSADOR_PROGRAM_CHOICES, label="Would you like to be part of the TCamp Ambassador Program?")
    class Meta:
        model = Ticket
        exclude = ['event', 'sale', 'success']

class PaymentForm(forms.Form):
    first_name = forms.CharField(max_length=255)
    last_name = forms.CharField(max_length=255)
    email = forms.EmailField()
    address1 = forms.CharField(max_length=1024, label="Address Line 1")
    address2 = forms.CharField(max_length=1024, label="Address Line 2", required=False)
    city = forms.CharField(max_length=255)
    state = forms.CharField(max_length=255, widget=us_forms.USStateSelect)
    zip = forms.CharField(max_length=255)

    exp_month = forms.ChoiceField(initial="01", label="Expiration", choices=(("01","01"),("02","02"),("03","03"),("04","04"),("05","05"),("06","06"),("07","07"),("08","08"),("09","09"),("10","10"),("11","11"),("12","12")))
    exp_year = forms.ChoiceField(initial="2014", label="Year", choices=(("2014","2014"),("2015","2015"),("2016","2016"),("2017","2017"),("2018","2018"),("2019","2019"),("2020","2020"),("2021","2021"),("2022","2022"),("2023","2023"),("2024","2024")))

    # will be encrypted
    number = forms.CharField(max_length=4096)
    cvv = forms.CharField(max_length=4096)