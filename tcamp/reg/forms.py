from django.forms import ModelForm

from reg.models import Sale, Ticket

class SaleForm(ModelForm):
    class Meta:
        model = Sale

class TicketForm(ModelForm):
    class Meta:
        model = Ticket