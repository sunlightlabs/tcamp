from django import forms

from reg.models import Sale, Ticket, AMBASSADOR_PROGRAM_CHOICES

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale

class TicketForm(forms.ModelForm):
    ambassador_program = forms.ChoiceField(initial="no", widget=forms.RadioSelect, choices=AMBASSADOR_PROGRAM_CHOICES, label="Would you like to be part of the TCamp Ambassador Program?")
    class Meta:
        model = Ticket
        exclude = ['event', 'sale', 'success']